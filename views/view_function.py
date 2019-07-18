from flask import jsonify
from flask.wrappers import Response
from models import ModelException
from typing import Callable, Tuple, Any

ViewFunctionReturnType = Tuple[Response, int]
ViewFunction = Callable[[], ViewFunctionReturnType]


def default_view_function(view_func: ViewFunction) -> ViewFunction:
    """
    Default API view wrapper to capture any ModelException and return a 400 Bad Request error code. Any other error is
     turned into a valid json and returned with a 500 Internal Server Error code

    :param view_func: original view function
    :return: wrapped view_func
    """
    def default_view_function_wrapper(*args, **kwargs):
        try:
            return view_func(*args, **kwargs)
        except ModelException as e:
            # In case an unhandled ModelException arises from view execution, a 400 Bad Request error code is returned
            return jsonify({'error': str(e)}), 400
        except BaseException as e:
            # In case an unkown unhandled Exception arises from view execution, a 500 Internal Server Error code
            #  is returned
            return jsonify({'error': str(e)}), 500

    return default_view_function_wrapper
