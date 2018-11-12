import logging
import json

from flask import Blueprint, request
from breakarticle.logic import svs_device_manager
from breakarticle.model.svs import Devices, DeviceDetailInfo
from breakarticle.model.svs import VendorModelDeviceMapping, Platforms
from breakarticle.model.svs import LibraryHash
from breakarticle.helper import api_ok, api_err, crossdomain
from breakarticle.forms import validate_json_schema
from breakarticle.forms import SyncSvsPatternForm

bp = Blueprint('svs.devices', __name__)

def _extract_ids_from_dn(dn_string):
    cn_string = dn_string.split(",")[1]
    (atom, device_id, vendor_key_id) = cn_string.split("|")
    return (device_id, vendor_key_id)

# Lack of validator.
@bp.route('svs/devices/touch', methods=['PUT', 'OPTIONS'])
def device_touch():
    req_data = request.get_json(force=True)
    logging.info(request.environ['DN'])
    (device_guid, vendor_key_id) = _extract_ids_from_dn(request.environ['DN'])
    logging.info("device: {}, vendor_id: {}".format(device_guid, vendor_key_id))

    hash_id = svs_device_manager.has_library_hash(req_data['library_hash'])
    baseline_diff = 'f' if hash_id else 't'
    collect_detail = True if req_data['collect_detail'] == 't' else False

    platform_id = svs_device_manager.get_platform_id(req_data['platform'])
    device_id = svs_device_manager.has_device(device_guid)
    if device_id is None:
        device_id = svs_device_manager.new_device(device_guid, collect_detail, platform_id)
        svs_device_manager.create_device_mapping(device_id,
                                                 vendor_key_id,
                                                 req_data['model_name'])
        logging.info("New device, information created")
    else:
        svs_device_manager.update_device(device_guid, collect_detail,
                                         platform_id)
        svs_device_manager.update_device_mapping(device_id,
                                                vendor_key_id,
                                                req_data['model_name'])
        logging.info("device existed, update information")

    results = {'baseline_diff': baseline_diff}
    return api_ok(**results)


@bp.route('/svs/devices/baseline', methods=['PUT', 'OPTIONS'])
def upload_device_baseline():
    json_data = request.get_json(force=True)
    (device_guid, vendor_key_id) = _extract_ids_from_dn(request.environ['DN'])

    from breakarticle.tasks import import_library_files #, find_all_cve
    device = Devices.query.filter_by(device_guid=device_guid).one()

    if device.locked:
        return api_accepted(), 202

    device.lock()
    #history = job_helper.create_job_history(device.id, 2)
    subtasks = []
    subtasks.append(import_library_files.si(device_guid, json_data))
    #subtasks.append(find_all_cve.si(device.id, history.id))

    from celery import chain
    chain(*subtasks).apply_async()

    results = {}
    return api_ok(**results)

@bp.route('/svs/devices/info', methods=['PUT', 'OPTIONS'])
def upload_device_info():
    json_data = request.get_json(force=True)
    (device_guid, vendor_key_id) = _extract_ids_from_dn(request.environ['DN'])

    from breakarticle.tasks import import_device_info
    import_device_info.delay(device_guid, json_data)

    results = {}
    return api_ok(**results)
