import logging

from flask import Blueprint
from breakarticle.logic import svs_pattern_manager, svs_library_manager
from breakarticle.model.svs import KnownLibraryVersion
from breakarticle.model.svs import KnownLibraryPattern
from breakarticle.helper import api_ok, api_err, crossdomain
from breakarticle.forms import validate_json_schema
from breakarticle.forms import SyncSvsPatternForm, SyncKnownLibrariesForm

bp = Blueprint('svs.patterns', __name__)


@bp.route('svs/patterns/version', methods=['GET', 'OPTIONS'])
def get_svs_pattern_version():
    results = dict()
    query_obj = KnownLibraryVersion.query.order_by(KnownLibraryVersion._ctime.desc()).first()
    if query_obj is not None:
        results['version'] = query_obj.version_hash
    else:
        results['version'] = ''
    logging.info(results)
    return api_ok(**results)


@bp.route('/svs/patterns', methods=['GET', 'OPTIONS'])
def get_svs_pattern():
    results = dict()
    results['static'] = []
    static_pattern_objs = KnownLibraryPattern.query.filter_by(
        lib_type=KnownLibraryPattern.LIBTYPE_STATIC
    ).all()
    for static_pattern_obj in static_pattern_objs:
        context = static_pattern_obj.context
        context['target'] = static_pattern_obj.target
        context['type'] = static_pattern_obj.static_type
        results['static'].append(context)

    results['dynamic'] = []
    dynamic_pattern_objs = KnownLibraryPattern.query.filter_by(
        lib_type=KnownLibraryPattern.LIBTYPE_DYNAMIC
    ).all()
    for dynamic_pattern_obj in dynamic_pattern_objs:
        context = dynamic_pattern_obj.context
        context['target'] = dynamic_pattern_obj.target
        results['dynamic'].append(context)

    return api_ok(**results)

@bp.route('/svs/internal/patterns', methods=['PUT', 'OPTIONS'])
@validate_json_schema(SyncSvsPatternForm)
def sync_pattern(form):
    result = svs_pattern_manager.sync_svs_pattern(form.static.data)
    zero_len = [len(x) == 0 for x in iter(result.values())]
    if all(zero_len):
        return api_err('NOT_MODIFIED'), 304
    else:
        return api_ok(data=result)

@bp.route('/svs/internal/known_libraries', methods=['PUT', 'OPTIONS'])
@validate_json_schema(SyncKnownLibrariesForm)
def sync_known_libraries(form):

    known_library_list = form.known_library_list.data
    result = svs_library_manager.sync_known_library(known_library_list)

    if len(result['known_library_added']) == 0:
        return api_err('NOT_MODIFIED'), 304

    return api_ok(data=result)
