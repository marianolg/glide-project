from data_access.data_accesor import DataAccessor, Model, ModelType
from typing import List, Hashable, Dict
import json


class InMemoryJsonFileDataAccessor(DataAccessor):
    """
    InMemoryJsonFileDataAccessor retrieves data from a json file with an array of objects of the type of the associated
    model. Receives the file_path on the __init__ method to read data from said file on instantiation.
    """

    def __init__(self, file_path: str):
        """
        Init method. Reads data from target Json file and stores it in memory in _raw_data attribute. It initializes the
        _data attribute with value None, it will be used later to hold the data by id and converted to the target model
        type

        :param file_path: Path to the json file holding the data
        """

        with open(file_path, 'r') as f:
            self._raw_data = json.load(f)
        self._data = None

    def _get_data(self, model_type: ModelType) -> Dict[Hashable, Model]:
        """
        Internal method to transform _raw_data values into _data dict that holds data formatted as target model type.
        If _data is None (first data access), it transforms the _raw_data into _data dict and deletes _raw_data from
        memory

        :param model_type: the class of the model whose data is being accessed
        :return: dict with models keys as keys, and models of type model_type as values
        """
        if self._data is None:
            self._data = {d[model_type.key_field_name()]: model_type(**d) for d in self._raw_data}
            del self._raw_data
        return self._data

    def _get_data_as_list(self, model_type: ModelType) -> List[Model]:
        """
        Internal method that returns all models in List form, form _data attribute (they are stored as a dict)

        :param model_type: the class of the model whose data is being accessed
        :return: list with models of type model_type
        """

        return list(self._get_data(model_type).values())

    def get(self, model_type: ModelType, limit: int = None, offset: int = None) -> List[Model]:
        """
        Fetches data from memory

        :param model_type: the class of the model whose data is being fetched
        :param limit: limits the number of objects to fetch. For this accessor, this is mandatory and should be >= 1.
        :param offset: offset value. If informed, start fetching data from this position
        :return: list of models of type model_type
        """

        off = offset if offset and offset > 0 else 0
        lim = (off + limit) if limit else None
        return self._get_data_as_list(model_type)[off:lim]

    def get_by_keys(self, model_type: ModelType, *keys: Hashable) -> List[Model]:
        """
        Fetch data from memory, by object keys

        :param model_type: the class of the model whose data is being fetched
        :param keys: inform 0 to n keys to fetch data from related objects
        :return: list of models of type model_type
        """

        data_by_key = self._get_data(model_type)
        return [data_by_key[k] for k in keys if k in data_by_key]
