from . import db
from sqlalchemy.dialects.postgresql import JSON
from sqlalchemy.sql import func
from sqlalchemy import Index
import logging

import datetime

# Library hash related tables

class LibraryHash(db.Model):
    __tablename__ = 'library_hash'
    hash_id = db.Column(db.Integer, primary_key=True)
    hash = db.Column(db.String(64), index=True, unique=True)

class HashLibraryFileMapping(db.Model):
    __tablename__ = 'hash_library_file_mapping'
    __table_args__ = (
                        db.PrimaryKeyConstraint('hash_library_id',
                                                'hash_library_files_id'),
                    )
    hash_library_id = db.Column(db.Integer, db.ForeignKey('hash_libraries.id'),
                                nullable=False)
    hash_library_files_id = db.Column(db.Integer,
                                      db.ForeignKey('hash_library_files.id'),
                                      nullable=False)


class HashLibraries(db.Model):
    __tablename__ = 'hash_libraries'
    id = db.Column(db.Integer, primary_key=True)
    hash_id = db.Column(db.Integer, db.ForeignKey('library_hash.hash_id'),
                        nullable=False)
    vendor = db.Column(db.String(256), nullable=False)
    app = db.Column(db.String(256), nullable=False)
    version = db.Column(db.String(256), nullable=False)
    _ctime = db.Column(db.DateTime(timezone=False),
                       default=datetime.datetime.utcnow)
    _mtime = db.Column(db.DateTime(timezone=False),
                       onupdate=datetime.datetime.utcnow,
                       default=datetime.datetime.utcnow)
    last_cve = db.Column(JSON, nullable=True)

    hash_library_files = db.relationship('HashLibraryFiles',
          secondary='hash_library_file_mapping',
          backref=db.backref('hash_libraries', lazy='dynamic'),
          lazy='dynamic')

    @property
    def cpe_name(self):
        return ':'.join((self.vendor, self.app, self.version))

    __table_args__ = (
        Index('idx_lib_hash_lib', 'hash_id', 'vendor', 'app', 'version'),
    )

class HashLibraryFiles(db.Model):
    __tablename__ = 'hash_library_files'
    id = db.Column(db.Integer, primary_key=True)
    hash_id = db.Column(db.Integer, db.ForeignKey('library_hash.hash_id'),
                        nullable=False)
    libname = db.Column(db.String(4096), nullable=False)
    path = db.Column(db.String(4096), nullable=False)
    _ctime = db.Column(db.DateTime(timezone=False),
                       default=datetime.datetime.utcnow)
    _mtime = db.Column(db.DateTime(timezone=False),
                       onupdate=datetime.datetime.utcnow,
                       default=datetime.datetime.utcnow)

class UnknownHashLibraries(db.Model):
    __tablename__ = 'unknown_hash_libraries'
    id = db.Column(db.Integer, primary_key=True)
    hash_id = db.Column(db.Integer, db.ForeignKey('library_hash.hash_id'),
                        nullable=False)
    libname = db.Column(db.String(4096), nullable=False)
    path = db.Column(db.String(4096), nullable=False)
    raw_version = db.Column(db.String(256), nullable=True)
    type = db.Column(db.Enum('unknown', 'suspect', name='lib_type'), nullable=False)
    _ctime = db.Column(db.DateTime(timezone=False),
                       default=datetime.datetime.utcnow)
    _mtime = db.Column(db.DateTime(timezone=False),
                       onupdate=datetime.datetime.utcnow,
                       default=datetime.datetime.utcnow)

class Vulnerabilities(db.Model):
    __tablename__ = 'vulnerabilities'
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    hash_id = db.Column(db.Integer, nullable=False)
    hash_library_id = db.Column(db.Integer, nullable=False)
    hash_library_file_id = db.Column(db.Integer, nullable=False)
    type = db.Column(db.String, nullable=False)
    name = db.Column(db.String, nullable=False)
    _ctime = db.Column(db.DateTime(timezone=False),
                       default=datetime.datetime.utcnow)
    _mtime = db.Column(db.DateTime(timezone=False),
                       onupdate=datetime.datetime.utcnow,
                       default=datetime.datetime.utcnow)


class JobHistory(db.Model):
    __tablename__ = 'job_history'
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    hash_id = db.Column(db.Integer, db.ForeignKey('library_hash.hash_id'), nullable=False)
    type = db.Column(db.Enum('regular', 'event', name='job_type'),
                     nullable=False)
    has_vulnerability = db.Column(db.Boolean, nullable=False)
    _ctime = db.Column(db.DateTime(timezone=False),
                       default=datetime.datetime.utcnow)
    _dtime = db.Column(db.DateTime(timezone=False),
                       default=datetime.datetime.utcnow)

class Schedules(db.Model):
    __tablename__ = 'schedules'
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    hash_id = db.Column(db.Integer, db.ForeignKey('library_hash.hash_id'), nullable=False)
    enabled = db.Column(db.Boolean, nullable=False, default=True)

    def disable(self):
        self.enabled = False
        db.session.commit()

    def enable(self):
        self.enabled = True
        db.session.commit()

    minute = db.Column(db.String(10))
    hour = db.Column(db.String(10))
    day_of_month = db.Column(db.String(10))
    month_of_year = db.Column(db.String(10))
    day_of_week = db.Column(db.String(10))
    _ctime = db.Column(db.DateTime(timezone=False),
                       default=datetime.datetime.utcnow)
    _mtime = db.Column(db.DateTime(timezone=False),
                       onupdate=datetime.datetime.utcnow,
                       default=datetime.datetime.utcnow)


# Device related tables

class Devices(db.Model):
    __tablename__ = 'devices'
    id = db.Column(db.Integer, primary_key=True)
    hash_id = db.Column(db.Integer, db.ForeignKey('library_hash.hash_id'),
                        nullable=True)
    locked = db.Column(db.Boolean, default=True, nullable=False)

    def lock(self):
        self.locked = True
        db.session.commit()

    def unlock(self):
        self.locked = False
        db.session.commit()

    device_guid = db.Column(db.String(64), nullable=False, index=True,
                            unique=True)
    collect_detail = db.Column(db.Boolean, default=False, nullable=False)
    platform_id = db.Column(db.Integer, db.ForeignKey('platforms.platform_id'), nullable=False)
    _ctime = db.Column(db.DateTime(timezone=False),
                       default=datetime.datetime.utcnow)
    _mtime = db.Column(db.DateTime(timezone=False),
                       onupdate=datetime.datetime.utcnow,
                       default=datetime.datetime.utcnow)

class Platforms(db.Model):
    __tablename__ = 'platforms'
    platform_id = db.Column(db.Integer, primary_key=True, nullable=False)
    platform_name = db.Column(db.String(64), nullable=False)
    memory_kb = db.Column(db.Integer, nullable=False)

class VendorModelDeviceMapping(db.Model):
    __tablename__ = 'vendor_model_device_mapping'
    device_id = db.Column(db.Integer, db.ForeignKey('devices.id'),
                          primary_key=True,
                          nullable=False)
    vendor_key_id = db.Column(db.String(64), nullable=False)
    model_name = db.Column(db.String(64), nullable=False)

class DeviceDetailInfo(db.Model):
   __tablename__ = 'device_detail_info'
   device_id = db.Column(db.Integer, db.ForeignKey('devices.id'),
                         primary_key=True,
                         nullable='False')
   detail = db.Column(JSON, nullable=True)

# SVS pattern related tables


class KnownLibraries(db.Model):
    __tablename__ = 'known_libraries'
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    vendor = db.Column(db.String(256), nullable=False)
    app = db.Column(db.String(256), nullable=False)
    _ctime = db.Column(db.DateTime(timezone=False),
                       default=datetime.datetime.utcnow)
    _mtime = db.Column(db.DateTime(timezone=False),
                       onupdate=datetime.datetime.utcnow,
                       default=datetime.datetime.utcnow)

    known_library_files = db.relationship('KnownLibraryFiles',
          secondary='known_library_file_mapping',
          backref=db.backref('known_libraries', lazy='dynamic'),
          lazy='dynamic')

    __table_args__ = (
        db.UniqueConstraint('vendor', 'app', name='vendor_app_unique_constraint'),
    )


class KnownLibraryFiles(db.Model):
    __tablename__ = 'known_library_files'
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    libname = db.Column(db.String(256), nullable=False)
    _ctime = db.Column(db.DateTime(timezone=False),
                       default=datetime.datetime.utcnow)
    _mtime = db.Column(db.DateTime(timezone=False),
                       onupdate=datetime.datetime.utcnow,
                       default=datetime.datetime.utcnow)


class KnownLibraryFileMapping(db.Model):
    __tablename__ = 'known_library_file_mapping'
    __table_args__ = (
                db.PrimaryKeyConstraint('known_libraries_id',
                                     'known_library_files_id'),
            )
    known_libraries_id = db.Column(db.Integer,
                                   db.ForeignKey('known_libraries.id'), nullable=False)
    known_library_files_id = db.Column(db.Integer,
                                   db.ForeignKey('known_library_files.id'), nullable=False)

class KnownLibraryVersion(db.Model):
    __tablename__ = 'known_library_version'
    _ctime = db.Column(db.DateTime(timezone=False), primary_key=True,
                       default=datetime.datetime.utcnow)
    version_hash = db.Column(db.String(64), nullable=False)

class KnownLibraryPattern(db.Model):
    __tablename__ = 'known_library_pattern'
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    lib_type = db.Column(db.Integer, nullable=False)
    target = db.Column(db.String(256), nullable=False)
    LIBTYPE_STATIC = 1
    LIBTYPE_DYNAMIC = 2
    context = db.Column(JSON, nullable=False)
    static_type = db.Column(db.Integer, nullable=False)
    STATIC_TYPE_LIB = 1
    STATIC_TYPE_EXE = 2

# DPI related table

class DpiUpdateStatus(db.Model):
    __tablename__ = 'dpi_update_status'
    pattern = db.Column(db.String(64), primary_key=True, nullable=False)
    type = db.Column(db.Enum('cve', 'keyword', name='pattern_type'),
                     nullable=False)
    _mtime = db.Column(db.DateTime(timezone=False),
                       default=datetime.datetime(1970, 1, 1, 0, 0, 0),
                       nullable=False)

