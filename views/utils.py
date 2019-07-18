from flask import request
from typing import Optional, List, Hashable


def get_int_query_param(param_name: str, raise_error: bool = False, default: int = None, min_value: int = None,
                        max_value: int = None) -> Optional[int]:
    """
    Util method that extracts an int value from query parameters

    :param param_name: name of the query parameter
    :param raise_error: defines it function should raise an excpetion in case of error.
     If False, just ignores the value in case of error
    :param default: default value in case query parameter is not present
    :param min_value: minimum value allowed. In case a value is informed and is less than this, it returns this value
    :param max_value: maximum value allowed. In case a value is informed and is greater than this, it returns this value
    :return: int value of parameter, or None
    """

    v = request.args.get(param_name)
    if v is None:
        return default

    try:
        value = int(v)
    except Exception as e:
        if raise_error:
            raise e
        value = default

    if value is None:
        return value

    return min(
        max_value if max_value is not None else value,
        max(
            min_value if min_value is not None else value,
            value,
        ),
    )


def get_list_query_param(param_name: str, raise_error: bool = False, remove_duplicates: bool = False) -> Optional[List]:
    """
    Util method that extracts a list from query parameters

    :param param_name: name of the query parameter
    :param raise_error: defines it function should raise an excpetion in case of error.
     If False, just ignores the value in case of error
    :param remove_duplicates: determines if duplicates should be removed from resulting list. It only works if all
     elements of the list ar Hashable. In case there is at least one non Hashable element, this is ignored
    :return: list of values
    """
    values = request.args.getlist(param_name)
    if not values:
        return None

    if remove_duplicates and not [1 for v in values if not isinstance(v, Hashable)]:
        return list(set(values))

    return values
