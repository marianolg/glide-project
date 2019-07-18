from data_access.data_accesor import DataAccessor, Model, ModelType
from typing import List, Hashable, Dict, Optional
from requests import get, ConnectTimeout, ConnectionError
import json


class JsonRestApiDataAccessor(DataAccessor):
    """
    JsonRestApiDataAccessor retrieves data from a restAPI using the endpoint configured on the __init__ method. The
    target API endpoint should be able to list objects of the associated model's type informing limit and offset params,
    ot list several specific objects by informing their ids (allowing more than on eid per request).
    """

    def __init__(self, endpoint: str, timeout: Optional[float] = 30.):
        """
        :param endpoint: url of endpoint from which data should be requested
        :param timeout: optional argument with timeout time in seconds for get requests (default is 30.). Can be None.
        """

        self._endpoint = endpoint
        self._timeout = timeout

    def _get(self, url: str) -> List[Dict]:
        """
        Internal method to fetch data from target API and return json parsed. Returns error if get requests' status
        code is != 200

        :param url: send request to this url
        :return: list of raw data in python dicts
        """

        try:
            response = get(url, timeout=self._timeout)
            if response.status_code != 200:
                raise ValueError(f'Error fetching data: {response.status_code} - {str(response.content or "")}')
            return json.loads(response.content)
        except ConnectTimeout:
            raise ConnectTimeout('Error fetching data: Connection timeout')
        except ConnectionError as e:
            raise ConnectionError(f'Error fetching data: Unexpected connection error: {str(e)}')

    def get(self, model_type: ModelType, limit: int = None, offset: int = None) -> List[Model]:
        """
        Fetches data from API

        :param model_type: the class of the model whose data is being fetched
        :param limit: limits the number of objects to fetch. For this accessor, this is mandatory and should be >= 1.
        :param offset: offset value. If informed, start fetching data from this position
        :return: list of models of type model_type
        """

        if limit is None or limit <= 0:
            raise ValueError(f'{self.__class__.__name__} requires limit >= 1 to get data')
        if offset and offset < 0:
            raise ValueError(f'{self.__class__.__name__} requires offset None or >= 0 to get data')

        return [
            model_type(**obj) for obj
            in self._get(f'{self._endpoint}?limit={limit}{f"&offset={offset}" if offset is not None else ""}')
        ]

    def get_by_keys(self, model_type: ModelType, *keys: Hashable) -> List[Model]:
        """
        Fetch data from API, by object keys

        :param model_type: the class of the model whose data is being fetched
        :param keys: inform 0 to n keys to fetch data from related objects
        :return: list of models of type model_type
        """

        return [
            model_type(**obj) for obj
            in self._get(f'{self._endpoint}?{"&".join([f"id={k}" for k in keys])}')
        ]
