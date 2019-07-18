from typing import NamedTuple, Any, Dict, Iterable, Hashable, Optional, List, Type
from models.fields import ModelField
from copy import deepcopy
from .exceptions import ModelException


ModelType = Type['Model']


class RelatedModelRequest(NamedTuple):
    related_model: ModelType
    next_level_relationships: List[str]


RelatedModelRequests = Dict[str, RelatedModelRequest]


class Model:
    _RELATIONSHIPS_SEPARATOR = '.'
    _data_accessor: 'DataAccessor' = None

    def __init__(self, **field_values) -> None:
        """
        Models base __init__ logic. Extract fields meta info from class variables and set validated data from received
        arguments
        """

        # Extract fields from class' existing class variables
        self.__fields = self.__class__._get_fields()

        if len([f for f in self.__fields.values() if f.is_key]) != 1:
            exception_type = Model.MultipleKeys if bool(len([f for f in self.__fields.values() if f.is_key])) \
                else Model.NoKey
            raise exception_type('Model needs to have one (and only one) key field.')

        # Check if any undefined field for the model was sent as a kwarg
        undefined_informed_fields = [fn for fn in field_values if fn not in self.__fields]
        if undefined_informed_fields:
            raise Model.UndefinedField(
                f'Unexpected value{"s" if len(undefined_informed_fields) > 1 else ""} informed for '
                f'{self.__class__.__name__}: "{", ".join(undefined_informed_fields)}"'
            )

        # Iterate through model's fields to set values, using Field's get_value method to properly set each value's type
        #  while performing basic validations
        for field_name, field in self.__fields.items():
            try:
                raise_error = None
                field.name = field_name
                setattr(self, field_name, field.get_value(field_values.get(field_name)))
            except ValueError as e:
                raise_error = ValueError(f'{field_name}: {e}')
            if raise_error:
                raise raise_error

    def __str__(self) -> str:
        return f'{self.__class__.__name__} object {str(self.key or "")}'.strip()

    def __repr__(self) -> str:
        return f'<{self.__class__.__name__}: {self}>'

    def __eq__(self, other):
        return self.__class__ == other.__class__ and bool(self.key) and self.key == other.key

    @classmethod
    def _get_fields(cls):
        return {f: v for f, v in cls.__dict__.items() if isinstance(v, ModelField)}

    @classmethod
    def key_field_name(cls) -> str:
        """Returns model's name of key field (Field with is_key = True)"""
        key__fields = [n for n, f in cls.__dict__.items() if isinstance(f, ModelField) and f.is_key]
        return key__fields[0] if key__fields else None

    @property
    def key(self) -> Any:
        """Returns objects's key value"""

        return getattr(self, self.__class__.key_field_name())

    @classmethod
    def _check_data_accessor_is_assigned(cls):
        """Checks if model has _data_accessor assigned and that it is of correct type (subclass of DataAccessor)"""
        from data_access import DataAccessor
        try:
            is_subclass_of_data_accessor = isinstance(cls._data_accessor, DataAccessor)
        except AttributeError:
            raise Model.WrongDataAccessor(
                f'_data_accessor class variable should be set to an object of type DataAccessor '
                f'on Model {cls.__name__}.'
            )
        if not is_subclass_of_data_accessor:
            raise Model.NoDataAccessor(f'_data_accessor should be of type DataAccessor on Model {cls.__name__}.')

    @classmethod
    def get(cls, limit: int = None, offset: int = None, with_related: Iterable[str] = None,
            **kwargs: Any) -> Iterable['Model']:
        """
        Data fetch method for Models, it calls its _data_accessor object. Fetches multiple objects.

        :param limit: if informed, limits the quantity of objects to fetch
        :param offset: offset value. If informed, start fetching data from this position
        :param with_related: list of related models to fetch (subsequent call to related models .get methods will be
         issued after successful fetch of current model's data)
        :param kwargs: any other arbitrary kwargs that the data accessor might need to retrieve the data
        :return: list (or other type of iterable) of models of type model_type
        """

        cls._check_data_accessor_is_assigned()
        return cls.get_related_models(
            cls._data_accessor.get(cls, limit=limit, offset=offset, **kwargs),
            *(with_related or []),
        )

    @classmethod
    def get_by_keys(cls, *keys: Hashable, with_related: Iterable[str] = None, **kwargs: Any) -> Iterable['Model']:
        """
        Data fetch method for Models, it calls its _data_accessor object. Fetches multiple objects by their keys.

        :param keys: inform 0 to n keys to fetch data from related objects
        :param with_related: list of related models to fetch (subsequent call to related models .get methods will be
         issued after successful fetch of current model's data)
        :param kwargs: any other arbitrary kwargs that the data accessor might need to retrieve the data
        :return: list (or other type of iterable) of models of type model_type
        """

        cls._check_data_accessor_is_assigned()
        if not keys:
            return []
        return cls.get_related_models(
            cls._data_accessor.get_by_keys(cls, *keys, **kwargs),
            *(with_related or []),
        )

    @classmethod
    def get_by_key(cls, key: Hashable, with_related: Iterable[str] = None, **kwargs: Any) -> Optional['Model']:
        """
        Data fetch method for Models, it calls its _data_accessor object. Fetches one object by key. Returns None if not
         found

        :param key: id of the model to retrieve from data
        :param with_related: list of related models to fetch (subsequent call to related models .get methods will be
         issued after successful fetch of current model's data)
        :param kwargs: any other arbitrary kwargs that the data accessor might need to retrieve the data
        :return: A model of type model_type, or None
        """

        cls._check_data_accessor_is_assigned()
        obj = cls._data_accessor.get_by_key(cls, key, **kwargs)
        if obj and with_related:
            return obj.get_related(*with_related)
        return obj

    @classmethod
    def _get_validated_relationships(cls, relationships: Iterable[str]) -> RelatedModelRequests:
        fields = cls._get_fields()
        normalized_related_models_request = {}
        for r in relationships:
            if len(r.split(Model._RELATIONSHIPS_SEPARATOR)) > 1:
                field_name, next_level_relationship = r.split(Model._RELATIONSHIPS_SEPARATOR, 1)
            else:
                field_name, next_level_relationship = [r, '']

            if field_name not in fields:
                raise Model.UndefinedField(f"{cls.__name__} has no '{field_name}' field")

            if field_name not in normalized_related_models_request:
                field = fields[field_name]
                field_type = field.get_related_model_field_type(cls)
                normalized_related_models_request[field_name] = RelatedModelRequest(
                    related_model=field_type,
                    next_level_relationships=[],
                )

            if next_level_relationship and \
                    next_level_relationship \
                    not in normalized_related_models_request[field_name].next_level_relationships:
                normalized_related_models_request[field_name].next_level_relationships.append(next_level_relationship)

        # Recursive validation of relationships
        for rel in normalized_related_models_request.values():
            rel.related_model._get_validated_relationships(rel.next_level_relationships)

        return normalized_related_models_request

    @classmethod
    def get_related_models(cls, objects: Iterable['Model'], *relationships: str) -> List['Model']:
        """
        Adds related models data to objects

        :param objects: base objects of current class. a copy of this objects will be returned, with additional data
        :param relationships: list of 0 to n relationships with other models. If accessing to level > 1 rel,
         should represent jump to next level with a '.'
        :return: a copy of the current objects including the related models data
        """

        # validated_relationships will hold a dict where each key is a field with a related_model whose related data
        #  should be fetched, and the value holds all of the next levels relationships for those fields (if any),
        #  to allow recursive access to this method to arbitrarily deep related data
        validated_relationships = cls._get_validated_relationships(relationships)

        # if no objects provided, or no relationships, the original objects can be returned in their original form
        if not objects or not relationships:
            return objects or []

        # new_objects dict will hold the copied objects to return. the objects' keys will be used as keys for the dict
        # to avoid processing duplicates and to mantain a hashed reference to each object for later references
        new_objects = {}
        # fetch_keys dict will hold a mapping dict for each related field, where the key will be the relationships
        #  target model key, and the value a list of the current objects keys that have that value for this field
        fetch_keys = {}
        for obj in objects:
            if obj.__class__ != cls:
                # If any object in the provided list is not ofthe current class type, the method will fail
                raise Model.IncorrectModelType(f'All objects should be an instance of {cls.__name__}.')

            if obj.key not in new_objects:  # avoid duplicates
                new_objects[obj.key] = deepcopy(obj)  # copy original objects into new_objects

                # Iterate through all of the requested related fields
                for field_name in validated_relationships:

                    if field_name not in fetch_keys:
                        # add the field_name key to the fetch_keys dict if not in there already
                        fetch_keys[field_name] = {}

                    # get the current obj value for the current field being processed
                    related_value = getattr(obj, field_name)

                    # if the current obj has a value for the current field, then add to the fetch keys dictionary for
                    #  the field (if not already in there), and add the current object to the related_object set.
                    #  If the related value is of type Model that would mean the related data is already available and
                    #  is then ignored to not be fetched again unnecessarily
                    if related_value is not None and not isinstance(related_value, Model):
                        if related_value not in fetch_keys[field_name]:
                            fetch_keys[field_name][related_value] = set()
                        fetch_keys[field_name][related_value].add(obj.key)

        # Iterate through all validated relationships to call the get_by_keys for each related model to fetch the needed
        #  objects of each type. Include the with_related=rel.next_level_relationships to recursively use this method to
        # fetch any deeper level related data that was requested
        for field_name, fetch_keys_relationship in fetch_keys.items():
            rel = validated_relationships[field_name]
            for related_model in rel.related_model.get_by_keys(
                    *fetch_keys_relationship.keys(),
                    with_related=rel.next_level_relationships,
            ):
                # Set the received object in the appropriate field in every oriignal object that had the key value for
                #  the field
                for target_object_key in fetch_keys_relationship[related_model.key]:
                    setattr(new_objects[target_object_key], field_name, related_model)

        return list(new_objects.values())

    def get_related(self, *relationships: str) -> 'Model':
        """
        Adds related models data to object

        :param relationships: list of 0 to n relationships with other models. If accessing to level > 1 rel,
         should represent jump to next level with a '.'
        :return: a copy of the current objects including the related models data
        """

        return self.__class__.get_related_models([self], *relationships)[0]

    def to_dict(self, exclude_none: bool = False) -> Dict[str, Any]:
        """
        Returns model's dict representation. If exclude_none is True, fields with None value won't be included in the
        resulting Dict
        """

        return {k: v if not isinstance(v, Model) else v.to_dict(exclude_none=exclude_none) for k, v in [
            (f, getattr(self, f)) for f in self.__fields
        ] if not exclude_none or v is not None}

    class MultipleKeys(ModelException):
        """Custom exception to signal that a Model has no more than one key field defined"""
        pass

    class NoKey(ModelException):
        """Custom exception to signal that a Model has no key field defined"""
        pass

    class UndefinedField(ModelException):
        """Custom exception to signal that a undefined field for the model is trying to be accessed"""
        pass

    class WrongDataAccessor(ModelException):
        """Custom exception to signal that a _data_accessor defined for a Model subclass is of wrong type"""
        pass

    class NoDataAccessor(ModelException):
        """Custom exception to signal that data is trying to be accessed for a model without a defined _data_accessor"""
        pass

    class IncorrectModelType(ModelException):
        """Custom exception to signal that an incorrect type of Model is being used"""
        pass
