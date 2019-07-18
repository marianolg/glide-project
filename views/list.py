from flask import request, jsonify
from models import ModelType
from .view_function import default_view_function, ViewFunctionReturnType
from .utils import get_int_query_param, get_list_query_param


@default_view_function
def list_view(model: ModelType, limit_param_name: str = 'limit', offset_param_name: str = 'offset',
              default_limit: int = 100, max_limit: int = 1000) -> ViewFunctionReturnType:
    """
    Default view to retrieve a list of objects of type model. It supports limit thq quantity of results, and the start
     offset. TODO A more complete version should support filters, ordering and advanced pagination

    :param model: the model of the objects to retrieve
    :param limit_param_name: name of query parameter to define the limit of objects to be returned
    :param offset_param_name: name of query parameter to define the start offset to retrieve objects from
    :param default_limit: default limit value. If not None, will be used whenever a limit value is not provided
    :param max_limit: maximum value of limit, in case a greater value of limit is provided, it is capped to this value
    :return: http response with either objects' data in JSON format and code 200 or error description and
     corresponding status error code
    """

    if request.method != 'GET':
        return jsonify({'error': f'Method {request.method} not allowed'}), 405

    return jsonify([o.to_dict() for o in model.get(
        limit=get_int_query_param(limit_param_name, default=default_limit, min_value=1, max_value=max_limit),
        offset=get_int_query_param(offset_param_name, min_value=0),
        with_related=get_list_query_param('expand', remove_duplicates=True),
    )])
