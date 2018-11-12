from . import db
from sqlalchemy.dialects.postgresql import JSON
import datetime


class DevicePatternStatus(db.Model):
    __tablename__ = 'device_pattern_status'
    id = db.Column(db.Integer, primary_key=True)
    device_id = db.Column(db.String(64), nullable=False, unique=True, index=True)
    pattern_status = db.Column(db.String(64), nullable=False)
    upload_pattern_id = db.Column(db.Integer, nullable=True)
    new_upload_pattern_id = db.Column(db.Integer, nullable=True)
    selected_pattern_id = db.Column(db.Integer, nullable=True)
    notified_pattern_id = db.Column(db.Integer, nullable=True)
    deployed_pattern_id = db.Column(db.Integer, nullable=True)
    deployed_error_code = db.Column(db.Integer, nullable=True)
    deployed_error_message = db.Column(db.String(256), nullable=True)
    deployed_time = db.Column(db.DateTime(timezone=False))
    _ctime = db.Column(db.DateTime(timezone=False), default=datetime.datetime.utcnow)
    _mtime = db.Column(db.DateTime(timezone=False), onupdate=datetime.datetime.utcnow, default=datetime.datetime.utcnow)


class UploadPattern(db.Model):
    __tablename__ = 'upload_patterns'
    id = db.Column(db.Integer, primary_key=True)
    device_id = db.Column(db.String(64), db.ForeignKey('device_pattern_status.device_id'), nullable=False)
    pattern_hash = db.Column(db.String(64), nullable=True)
    _ctime = db.Column(db.DateTime(timezone=False), default=datetime.datetime.utcnow)
    _mtime = db.Column(db.DateTime(timezone=False), onupdate=datetime.datetime.utcnow, default=datetime.datetime.utcnow)


class PatternhHistory(db.Model):
    __tablename__ = 'pattern_history'
    id = db.Column(db.Integer, primary_key=True)
    device_id = db.Column(db.String(64), db.ForeignKey('device_pattern_status.device_id'), nullable=False)
    pattern_hash = db.Column(db.String(64), nullable=True)
    _ctime = db.Column(db.DateTime(timezone=False), default=datetime.datetime.utcnow)


class DpiRequests(db.Model):
    __tablename__ = 'dpi_requests'
    pattern_id = db.Column(db.Integer, primary_key=True, index=True)
    request_number = db.Column(db.String(32), nullable=False, unique=True, index=True)
    request_status = db.Column(db.String(16), nullable=False)
    download_link = db.Column(db.String(512), nullable=True)
    checksum = db.Column(db.String(64), nullable=True)
    session_token = db.Column(db.String(64), nullable=True)
    _mtime = db.Column(db.DateTime(timezone=False), onupdate=datetime.datetime.utcnow, default=datetime.datetime.utcnow)


class DpiPattern(db.Model):
    __tablename__ = 'dpi_pattern'
    pattern_id = db.Column(db.Integer, db.ForeignKey('dpi_requests.pattern_id'), primary_key=True)
    pattern_hash = db.Column(db.String(64), nullable=False)
    library_hash = db.Column(db.String(64), nullable=True)
    fix_cve_ids = db.Column(JSON, nullable=True)
    memory_kb = db.Column(db.Integer, nullable=True)
    platform = db.Column(db.String(64), nullable=True)
    _ctime = db.Column(db.DateTime(timezone=False), default=datetime.datetime.utcnow)
    _mtime = db.Column(db.DateTime(timezone=False), onupdate=datetime.datetime.utcnow, default=datetime.datetime.utcnow)

