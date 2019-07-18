from models import Model, ModelType
from typing import Hashable, Union, Iterable


class DataAccessor:
    """Base DataAccessor class. All specific DataAccessors should inherit from this class."""

    def get(self, model_type: ModelType, limit: int = None, offset: int = None) -> Iterable[Model]:
        """
        Base fetch data method for DataAccessors

        :param model_type: the class of the model whose data is being fetched
        :param limit: if informed, limits the quantity of objects to fetch
        :param offset: offset value. If informed, start fetching data from this position
        :return: list (or other type of iterable) of models of type model_type
        """

        raise NotImplementedError

    def get_by_keys(self, model_type: ModelType, *keys: Hashable) -> Iterable[Model]:
        """
        Base fetch data by ids method for DataAccessors

        :param model_type: the class of the model whose data is being fetched
        :param keys: inform 0 to n keys to fetch data from related objects
        :return: list (or other type of iterable) of models of type model_type
        """

        raise NotImplementedError

    def get_by_key(self, model_type: ModelType, key: Hashable) -> Union[Model, None]:
        """
        Base fetch data by key method for DataAccessors. It returns the model for the informed key or None if not found.

        :param model_type: the class of the model whose data is being fetched
        :param key: id of the model to retrieve from data
        :return: A model of type model_type, or None
        """

        results = self.get_by_keys(model_type, key)
        return results[0] if results else None
