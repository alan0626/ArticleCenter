from breakarticle.model import db
from breakarticle.model.svs import Devices, DeviceDetailInfo
from .factory import create_celery_app

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

