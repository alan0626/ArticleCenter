from breakarticle.model import db
from breakarticle.model.svs import KnownLibraryFiles, KnownLibraries
from breakarticle.model.svs import HashLibraries, HashLibraryFiles
from breakarticle.model.svs import UnknownHashLibraries, Vulnerabilities
import logging


def query_insert_hash_library(hash_id, known_libraries, version, commit=False):
    hash_library_list = []
    for known_library in known_libraries:
        hash_library = HashLibraries.query.filter_by(
            hash_id=hash_id,
            vendor=known_library.vendor,
            app=known_library.app,
            version=version
        ).first()
        if hash_library is None:
            hash_library = HashLibraries(
                hash_id=hash_id,
                vendor=known_library.vendor,
                app=known_library.app,
                version=version
            )
            db.session.add(hash_library)
        hash_library_list.append(hash_library)
    if commit:
        db.session.commit()
    return hash_library_list


def query_insert_hash_library_files(hash_id, hash_library_list, libname, path, commit=False):
    hash_library_file = HashLibraryFiles.query.filter_by(
        hash_id=hash_id,
        libname=libname,
        path=path
    ).first()
    if hash_library_file is None:
        hash_library_file = HashLibraryFiles(
            hash_id=hash_id,
            libname=libname,
            path=path,
            hash_libraries=hash_library_list
        )
        db.session.add(hash_library_file)
    if commit:
        db.session.commit()
    return hash_library_file


def query_insert_unknown_hash_library(hash_id, type, libname, path, version, commit=False):
    unknown_hash_library = UnknownHashLibraries.query.filter_by(
        hash_id=hash_id,
        type=type,
        libname=libname,
        path=path
    ).first()
    if unknown_hash_library is None:
        unknown_hash_library = UnknownHashLibraries(
            hash_id=hash_id,
            type=type,
            libname=libname,
            path=path,
            raw_version=version
        )
        db.session.add(unknown_hash_library)
    if commit:
        db.session.commit()
    return unknown_hash_library


def delete_hash_libraries(hash_id, commit=False):
    for obj in Vulnerabilities.query.filter_by(hash_id=hash_id).yield_per(100).enable_eagerloads(False):
        db.session.delete(obj)
    for obj in HashLibraryFiles.query.filter_by(hash_id=hash_id).yield_per(100).enable_eagerloads(False):
        db.session.delete(obj)
    for obj in HashLibraries.query.filter_by(hash_id=hash_id).yield_per(100).enable_eagerloads(False):
        db.session.delete(obj)
    for obj in UnknownHashLibraries.query.filter_by(hash_id=hash_id).yield_per(100).enable_eagerloads(False):
        db.session.delete(obj)
    if commit:
        db.session.commit()

def sync_known_library(known_library_list, commit=True):

    result = dict(
        known_library_added=[],
    )

    # Check for add
    for lib in known_library_list:
        known_lib_file = KnownLibraryFiles.query.filter_by(libname=lib['libname']).first()
        if known_lib_file is None:
            known_lib = KnownLibraries.query.filter_by(vendor=lib['vendor'], app=lib['app']).first()
            if known_lib is None: # Add new library
                k = KnownLibraries(vendor=lib['vendor'], app=lib['app'])
            else:
                k = known_lib # Add library file with existing library
            logging.info("Importing Known Library File... libname: {}".format(lib['libname']))
            known_lib_file = KnownLibraryFiles(libname=lib['libname'], known_libraries=[k])
            db.session.add(known_lib_file)
            result['known_library_added'].append(dict(
                vendor=lib['vendor'],
                app=lib['app'],
                libname=lib['libname']
            ))
        else:
            known_lib = KnownLibraries.query.filter_by(vendor=lib['vendor'], app=lib['app']).first()
            if known_lib is None:
                k = KnownLibraries(vendor=lib['vendor'], app=lib['app'], known_library_files=[known_lib_file])
                logging.info("Importing Known Library File... libname: {}".format(lib['libname']))
                db.session.add(k)
                result['known_library_added'].append(dict(
                    vendor=lib['vendor'],
                    app=lib['app'],
                    libname=lib['libname']
                ))
            else:
                # vendor, app, libname pair already exist, skip this one
                pass

    if commit:
        db.session.commit()

    return result

