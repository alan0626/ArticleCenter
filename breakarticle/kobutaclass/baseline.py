from breakarticle.model import db
from breakarticle.model.svs import Devices, KnownLibraryFiles, DeviceDetailInfo
from breakarticle.logic.svs_library_manager import query_insert_hash_library
from breakarticle.logic.svs_library_manager import query_insert_hash_library_files
from breakarticle.logic.svs_library_manager import query_insert_unknown_hash_library
from breakarticle.logic.svs_library_manager import delete_hash_libraries
from breakarticle.logic.svs_device_manager import has_library_hash, new_library_hash
from breakarticle.exceptions import AtomNotFoundError
import logging

from breakarticle.kobutaclass.observable import Observable

class ObservableBaseline(Observable):
    """
    Baseline class, handle import and schedule tasks
    """

    TYPE = ['known', 'suspect', 'unknown']

    def __init__(self, hash_id, json_body):
        super(ObservableBaseline, self).__init__()
        if hash_id is None or json_body is None:
            raise AtomNotFoundError(message="You must provide hash_id & json_body for baseline class")
        self.hash_id = hash_id
        self.json_body = json_body

    def process(self):
        self._replace_baseline()
        db.session.commit()

        return self

    def _import_baseline(self):
        for type in self.TYPE:
            logging.warn('%s in json_data', (type))
            file_list = self.json_body[type]
            mis_identified_lib_files = []
            for idx, entry in enumerate(file_list):
                if type == 'known':
                    known_lib_file = KnownLibraryFiles.query.filter_by(libname=entry['libname']).first()
                    if known_lib_file is not None:
                        known_library_list = [x for x in known_lib_file.known_libraries]
                        hash_library_list = query_insert_hash_library(self.hash_id, known_library_list, entry['version'])
                        #logging("Known library list: {}".format(hash_library_list))
                        query_insert_hash_library_files(self.hash_id, hash_library_list, entry['libname'], entry['path'])
                else:
                    known_lib_files_as_mis_identified = KnownLibraryFiles.query.filter_by(libname=entry['libname']).all()
                    if len(known_lib_files_as_mis_identified) > 0:
                        logging.info("Found one mis-identified library : {} in {} list".format(entry['libname'], type))
                        mis_identified_lib_files.append(entry)
                    query_insert_unknown_hash_library(self.hash_id, type, entry['libname'], entry['path'], entry['version'])

                if idx > 0 and idx % 100 == 0:
                    db.session.flush()

    def _replace_baseline(self):
        logging.warn("Replacing hash baseline......")
        self._delete_libraries()
        self._import_baseline()

    def _delete_libraries(self):
        delete_hash_libraries(self.hash_id, commit=True)

    @staticmethod
    def get_device_object(device_id):
        device = Devices.query.filter_by(id=device_id).first()
        if device is None:
            raise AtomNotFoundError(message="Device id :{} not found".format(device_id))
        return device
