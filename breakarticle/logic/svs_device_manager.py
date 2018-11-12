from breakarticle.model import db
from breakarticle.model.svs import LibraryHash, Devices, Platforms, VendorModelDeviceMapping
import json
import hashlib
import logging

def new_library_hash(library_hash):
    lh_obj = LibraryHash(hash=library_hash)
    db.session.add(lh_obj)
    db.session.flush()
    db.session.commit()
    return lh_obj.hash_id

def has_library_hash(library_hash):
    lh = LibraryHash.query.filter_by(hash=library_hash).first()
    if lh:
        return lh.hash_id
    return None

def _new_platform(platform):
    pf_obj = Platforms(platform_name=platform, memory_kb=4096)
    db.session.add(pf_obj)
    db.session.flush()
    db.session.commit()
    logging.info(pf_obj)
    return pf_obj.platform_id

def get_platform_id(platform):
    pf = Platforms.query.filter_by(platform_name=platform).first()
    if pf:
        return pf.platform_id
    else:
        return _new_platform(platform)

def has_device(device_guid):
    dev = Devices.query.filter_by(device_guid=device_guid).first()
    if dev:
        return dev.id
    return None

def new_device(device_guid, collect_detail, platform_id):
    default_locked = False
    dev_obj = Devices(device_guid=device_guid, collect_detail=collect_detail,
                      platform_id=platform_id, locked=default_locked)
    db.session.add(dev_obj)
    db.session.flush()
    db.session.commit()
    return dev_obj.id

def update_device(device_guid, collect_detail, platform_id):
    dev = Devices.query.filter_by(device_guid=device_guid).first()
    if dev:
        dev.collect_detail = collect_detail
        dev.platform_id  = platform_id
        db.session.commit()
        return True
    return False


def create_device_mapping(device_id, vendor_key_id, model_name):
    vmdm_obj = VendorModelDeviceMapping(device_id=device_id,
                                        vendor_key_id=vendor_key_id,
                                        model_name=model_name)
    db.session.add(vmdm_obj)
    db.session.commit()
    return True

def update_device_mapping(device_id, vendor_key_id, model_name):
    vmdm = VendorModelDeviceMapping.query.filter_by(device_id=device_id).first()
    if vmdm:
        vmdm.vendor_key_id = vendor_key_id
        vmdm.model_name = model_name
        db.session.commit()
        return True
    return False

