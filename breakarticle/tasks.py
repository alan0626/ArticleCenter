from breakarticle.model import db
from breakarticle.model.svs import Devices, DeviceDetailInfo
from breakarticle.model.svs import LibraryHash
from celery import chord
from celery.schedules import crontab_parser
from celery.signals import worker_process_init, worker_process_shutdown
from .factory import create_celery_app

from breakarticle.kobutaclass.baseline import ObservableBaseline
from breakarticle.kobutaclass.observer.observers import SchedulerObserver, DeviceFinishBaselineUploadObserver
from breakarticle.logic.svs_device_manager import has_library_hash, new_library_hash

import json
import logging


celery = create_celery_app()

@celery.task(ignore_result=False)
def import_device_info(device_guid, json_body):
    device = Devices.query.filter_by(device_guid=device_guid).first()
    device_info = DeviceDetailInfo.query.filter_by(device_id=device.id).first()
    if device_info:
        device_info.detail = json.dumps(json_body)
        logging.info("Device ID: {} - Device detail updated.".format(device.id))
    else:
        device_info_obj = DeviceDetailInfo(device_id=device.id, detail=json.dumps(json_body))
        db.session.add(device_info_obj)
        logging.info("Device ID: {} - Device detail created.".format(device.id))
    db.session.commit()


@celery.task(ignore_result=True)
def import_library_files(device_guid, json_body):
    try:
        library_hash = json_body['library_hash']
        hash_id = has_library_hash(library_hash)
        if hash_id is None:
            hash_id = new_library_hash(library_hash)
        ob_baseline = ObservableBaseline(hash_id=hash_id, json_body=json_body)
        # Register all observer callback
        SchedulerObserver(hash_id=hash_id).register(observable=ob_baseline)
        DeviceFinishBaselineUploadObserver(hash_id=hash_id).register(observable=ob_baseline)
        # Import!
        ob_baseline.process().notify_observers()
    except sqlalchemy.exc.IntegrityError as e:
        db.session.rollback()
        logging.error(e)
    except Exception as e:
        logging.exception(e)
