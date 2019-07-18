from flask import request, jsonify
from typing import Hashable
from models import ModelType
from .view_function import default_view_function, ViewFunctionReturnType
from .utils import get_list_query_param


@default_view_function
def retrieve_view(model: ModelType, key: Hashable) -> ViewFunctionReturnType:
    """
    Default view to retrieve a single object of type model, given its key. It returns 404 if does not exist

    :param model: the model of the object to retrieve
    :param key: the key of the object to retrieve
    :return: http response with either object's data in JSON format and code 200 or error description and
     corresponding status error code
    """

    if request.method != 'GET':
        return jsonify({'error': f'Method {request.method} not allowed'}), 405

    obj = model.get_by_key(key, with_related=get_list_query_param('expand', remove_duplicates=True))

    if not obj:
        return jsonify({'error': 'Not found'}), 404

    return jsonify(obj.to_dict())
