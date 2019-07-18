from flask.testing import FlaskClient
from models import ModelType
from typing import Iterable, Hashable
import json


def sorted_by_id(lst: Iterable[dict]) -> Iterable:
    """
    Returns sorted list of dicts ordered by id. This sorting logic is used several times accross test, and is
    therefore extracted
    """

    return sorted(lst, key=lambda elem: elem.get('id'))


def _test_retrieve_model(client: FlaskClient, url: str, model: ModelType, key: Hashable, **get_kwargs) -> None:
    """
    Default test of retrieve object view.

    :param client: Flask testing client
    :param url: url to test
    :param model: model to retrieve
    :param key: key of object to retrieve
    :param get_kwargs: other kwargs that the model might need for retrieving
    :return: None
    """

    resp = client.get(url)
    assert resp.status_code is 200
    assert json.loads(resp.data) == model.get_by_key(key, **get_kwargs).to_dict()


def _test_retrieve_model_not_found(client: FlaskClient, url: str) -> None:
    """
        Default test of retrieve object view, for not found object.

        :param client: Flask testing client
        :param url: url to test
        :return: None
        """

    resp = client.get(url)
    assert resp.status_code == 404


def _test_list_model(client: FlaskClient, url: str, model: ModelType, **get_kwargs) -> None:
    """
    Default test of list objects view.

    :param client: Flask testing client
    :param url: url to test
    :param model: model to retrieve
    :param get_kwargs: other kwargs that the model might need for retrieving
    :return: None
    """

    resp = client.get(url)
    assert resp.status_code is 200
    assert sorted_by_id(json.loads(resp.data)) == sorted_by_id([o.to_dict() for o in model.get(**get_kwargs)])
