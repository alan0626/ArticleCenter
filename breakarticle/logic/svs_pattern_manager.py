from breakarticle.model import db
from breakarticle.model.svs import KnownLibraryPattern
from breakarticle.model.svs import KnownLibraryVersion
import json
import hashlib
import logging


def sync_svs_pattern(static_pattern_list_input):
    """
    :param static_pattern_list_input:
    :param dynamic_pattern_list_input:
    :return:
    """

    def _create_result(lib_pattern):
        """
        Pretty printing of ORM objects.

        Used only for debug message and API results.
        The string representation from the ORM objects are not helpful.
        """
        return {
            'target': lib_pattern.target,
            'section': lib_pattern.context['section'],
            'pattern': lib_pattern.context['pattern'],
            'type': lib_pattern.static_type,
        }

    result = dict(
        static_pattern_added=[],
        static_pattern_deleted=[],
        static_pattern_changed=[],
    )


    m = dict((sp['target'], sp) for sp in static_pattern_list_input)
    current_patterns = KnownLibraryPattern.query.filter_by(
        lib_type=KnownLibraryPattern.LIBTYPE_STATIC,
    ).all()

    for cp in current_patterns:
        if cp.target in m:
            sp_obj = m[cp.target]
            vec = [True, True]

            if sp_obj['type'] != cp.static_type:
                cp.static_type = sp_obj['type']
                vec[0] = False

            if sp_obj['section'] != cp.context['section'] or \
                sp_obj['pattern'] != cp.context['pattern']:
                new_context = {
                    'section': sp_obj['section'],
                    'pattern': sp_obj['pattern'],
                }
                cp.context = new_context
                vec[1] = False

            if not all(vec):
                logging.info("Update pattern: {}".format(str(sp_obj)))
                result['static_pattern_changed'].append(_create_result(cp))

            # We've finished this one
            del m[cp.target]
        else:
            # We keep old data to maintain foreign key refrencing completes
            pass
            # logging.info("Deleteing static pattern... libname: {}".format(_create_result(cp)))
            # result['static_pattern_deleted'].append(_create_result(cp))
            # db.session.delete(cp)

    for to_add in iter(m.values()):
        context = {
            'section': to_add['section'],
            'pattern': to_add['pattern']
        }
        new_p = KnownLibraryPattern(
            lib_type=KnownLibraryPattern.LIBTYPE_STATIC,
            target=to_add['target'],
            static_type=to_add['type'],
            context=context
        )
        logging.info("Importing static pattern... libname: {}".format(_create_result(new_p)))
        result['static_pattern_added'].append(_create_result(new_p))
        db.session.add(new_p)

    # Generate unique sha1 for new SVS pattern
    sorted_new_pattern = sorted(static_pattern_list_input, key=lambda k: k['target'])
    sha1_handler = hashlib.sha1()
    sha1_handler.update(json.dumps(sorted_new_pattern).encode('utf-8'))
    new_pattern_sha1 = sha1_handler.hexdigest()

    current_pattern_sha1 = ''
    query_obj = KnownLibraryVersion.query.order_by(KnownLibraryVersion._ctime.desc()).first()
    if query_obj is not None:
        current_pattern_sha1 = query_obj.version_hash

    if current_pattern_sha1 != new_pattern_sha1:
        db.session.add(KnownLibraryVersion(version_hash=new_pattern_sha1))
        logging.info("OLD pattern sha1 hash: %s" % current_pattern_sha1)
        logging.info("New pattern sha1 hash: %s" % new_pattern_sha1)

    db.session.commit()

    return result
