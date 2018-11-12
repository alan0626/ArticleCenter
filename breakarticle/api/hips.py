from flask import Blueprint, request
import requests
import logging
import ast
import json
from breakarticle.exceptions import AtomAddPatternFailedError
from breakarticle.exceptions import AtomDeviceDuplicateError
from breakarticle.exceptions import AtomPatternDuplicateError
from breakarticle.exceptions import AtomTwoWaySSLUnauthorizedError
from breakarticle.exceptions import AtomMQTTConnectionError
from breakarticle.exceptions import AtomInvalidFilenameError
from breakarticle.helper import api_ok, api_err
from breakarticle.forms import validate_pattern_file_schema, validate_json_schema
from breakarticle.forms import AddPatternForm, DeploymentForm
from breakarticle.articleclass import pattern_manager, s3
from breakarticle.articleclass.generate_pattern import GeneratePattern
from breakarticle.articleclass.pattern_manager import TmpZippedPattern
from breakarticle.model.hips import DevicePatternStatus, UploadPattern

bp = Blueprint('hips', __name__)


@bp.errorhandler(AtomAddPatternFailedError)
@bp.errorhandler(AtomMQTTConnectionError)
def wrong_pattern_action_handler(err):
    return api_err('INTERNAL_ERROR', message=err.message)


@bp.errorhandler(AtomTwoWaySSLUnauthorizedError)
@bp.errorhandler(AtomInvalidFilenameError)
def twoway_auth_error_handler(err):
    return api_err('BAD_REQUEST', message=err.message)


@bp.errorhandler(AtomDeviceDuplicateError)
@bp.errorhandler(AtomPatternDuplicateError)
def resource_duplicate_handler(err):
    return api_err('CONFLICT', message=err.message)


# Upload new pattern
@bp.route('/hips/internal/devices/<uuid:device_id>/patterns/upload', methods=['POST', 'OPTIONS'])
@validate_pattern_file_schema(AddPatternForm)
def upload_pattern(device_id, form, pattern_file):
    # TODO: Change: initial device info to database
    logging.info("Louis_Pattern")
    pattern_manager.init_pattern(device_id)
    device = DevicePatternStatus.query.filter_by(device_id=str(device_id)).first()
    if device is None:
        raise AtomAddPatternFailedError("Cannot add pattern to non-existing device: device_id = {}".format(device_id))

    # Validate filename
    pattern_manager.validate_pattern_filename(pattern_file.filename)
    if not pattern_manager.validate_ext_filename(pattern_file.filename, ['zip']):
        raise AtomInvalidFilenameError

    tmp_file_obj = TmpZippedPattern(pattern_file)
    with tmp_file_obj:
        tmp_file_obj.validate_archive()
        # Upload S3
        s3_object_key, res = s3.upload_pattern(form.vendor_key_id.data, device_id, tmp_file_obj)

        if res['ResponseMetadata']['HTTPStatusCode'] == 200:
            logging.debug("Pattern : {} successfully uploaded to S3 : {} ".format(pattern_file.filename, s3_object_key))
            pattern_manager.add_pattern(device_id, tmp_file_obj.pattern_zip_hash)
            return api_ok(bucket=s3_object_key)
        else:
            return api_err(message="Upload to S3 failed, code = {}".format(res['ResponseMetadata']['HTTPStatusCode']))


@bp.route('/hips/internal/devices/patterns/deployment', methods=['POST', 'OPTIONS'])
@validate_json_schema(DeploymentForm)
def deploy_pattern(form):
    device_dict = ast.literal_eval(form.device.data)
    confirm_list = {'to_be_submitted': [], 'pattern_not_found': []}
    pattern_not_found = []
    submitted_list = []
    for key, value in device_dict.items():
        devices_list = UploadPattern.query.filter_by(device_id=key).all()
        if devices_list:
            for devices in devices_list:
                if devices.pattern_hash == value:
                    submitted_list.append(devices.device_id)
                    pattern_manager.deploying_pattern(devices.device_id, devices.id)
            if devices.device_id not in submitted_list:
                pattern_not_found.append(devices.device_id)
        else:
            pattern_not_found.append(key)
    confirm_list['to_be_submitted'] = submitted_list
    confirm_list['pattern_not_found'] = pattern_not_found
    pattern_manager.notify_devices_mqtt(form.vendor_key_id.data, submitted_list, retain=False)
    return api_ok(**confirm_list)


@bp.route('/hips/dpi/callback2', methods=['POST', 'OPTIONS'])
def dpi_callback2():
    # request_status: 'pending', 'requested', 'done', 'failed'
    dpi_json = request.get_data()
    # j_data =  json.loads(dpi_json)
    logging.info("dpi : {}".format(dpi_json))
    return api_ok("OK")


@bp.route('/hips/dpi/generate_pattern', methods=['POST', 'OPTIONS'])
def dpi_generate_pattern():
    """
    # request_status: 'pending', 'requested', 'done', 'failed'
    dpi_json = request.get_data()
    # j_data =  json.loads(dpi_json)
    logging.info("dpi : {}".format(dpi_json))
    return api_ok("OK")
    """
    query_key_list = ["CVE-2016-3714", "CVE-2111-1234"]
    device_guid = "fd8ba679-7d96-4fda-885e-beac73246e09"
    pattern_service = GeneratePattern()
    pattern_info = pattern_service.constitute_info(device_guid, query_key_list)
    r_query = pattern_service.request_pattern(pattern_info)
    if r_query.status_code == 200:
        query_result = json.loads(s=r_query.text)
        security_confrim_list = []
        for security_list in query_result["SecurityList"]["a_security_list"]:
            if security_list["i_state"] == 1:
                security_confrim_list.append(security_list["s_security_name"])
        if query_result["SecurityList"]["i_supported_list"] == len(security_confrim_list):
            # request action: 1=query 2=packing
            request_action = 2
            pattern_confirm__info = pattern_service.constitute_info(device_guid, query_key_list, request_action)
            pattern_service.request_pattern(pattern_confirm__info, request_action)
        else:
            logging.debug('DPI queried list do not match, supported_count {}, security_confirm_count: {}'
                          .format(query_result["SecurityList"]["i_supported_list"], len(security_confrim_list)))
        logging.info('Louis_DPI queried list do not match, supported_count {}, security_confrim_count: {}'
                      .format(query_result["SecurityList"]["i_supported_list"], len(security_confrim_list)))
    else:
        logging.debug('DPI queried list was failed, status_code {}'.format(r.status_code))
    return api_ok("OK")


@bp.route('/hips/dpi/callback', methods=['POST', 'OPTIONS'])
def dpi_pattern_callback():
    # request_status: 'pending', 'requested', 'done', 'failed'
    dpi_json = request.get_data()
    dpi_data = json.loads(dpi_json)
    if dpi_data["SigInfo"]["i_sig_response"] == 0:
        prefix_url = "http://10.205.16.170/DPISIG/Project/ATOM-V2/"
        pattern_name = dpi_data["SigInfo"]["s_sig_name"] + "-" + str(dpi_data["SigInfo"]["i_sig_ver_major"]) + "." \
                       + str(dpi_data["SigInfo"]["i_sig_ver_minor"]) + "-DPI.zip"
        r = requests.get(prefix_url + str(dpi_data["SigInfo"]["s_request_number"] + "/" + pattern_name))
        with open(pattern_name, "wb") as code:
            code.write(r.content)
        logging.info("pattern_name : {}".format(pattern_name))

    with open(pattern_name, 'rb') as f:
        payload = {}
        file = {'file': f}
        device_id = "fd8ba679-7d96-4fda-885e-beac73246e09"
        proxies = {
            "http": "http://10.1.212.51:8080"
        }
        url = "http://ts-monitor.atom.trendmicro.com:8880/v0/hips/internal/devices/" + device_id + "/patterns/upload"
        logging.info("louis_url: {}".format(url))
        r = requests.post(url, data=payload, files=file, proxies=proxies)
        if r.status_code == 200:
            json_resp = json.loads(r.text)
            logging.info("DPI upload complete, bucket name : {}".format(json_resp['data']))
            return api_ok("OK")
        else:
            logging.info("DPI upload Failed without server message : status_code = {}".format(r.status_code))
            return api_err(message="DPI Upload to S3 failed, code = {}".format(r.status_code))
