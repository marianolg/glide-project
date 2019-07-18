from typing import Any, Hashable, Union, Type, Optional
from .exceptions import ModelException


# RelatedModels can either be a Model Subclass or a str with the name of a Model Subclass, or the special value 'self'
RelatedModel = Union[Type['Model'], str]


class ModelField:
    """
    Base ModelField class. Represents a model's field, has a type. Is Subclassed for types specific treatments
    """

    def __init__(self, field_type: type, nullable: bool = False, is_key: bool = False,
                 related_model: RelatedModel = None):
        """

        :param field_type: type of the field. Is any valid Python type
        :param nullable: defines is field can be of value None for the Model. key fields can always be None
         regardless of this arg, in order to allow null values on non stored models (for cases in which the key value
         is determined once stored)
        :param is_key: defines if a field is the key field within its model
        :param related_model: defines the field as a key of another model to establish a relationship. These fields
         still have their own type, which should match that of the related_model's key
        """

        if (is_key or related_model is not None) and not isinstance(field_type, Hashable):
            raise ModelField.WrongfFieldType(
                f'Key fields and fields with related_mode should be of a Hashable type. '
                f'{field_type.__name__} is not Hashable'
            )
        self.field_type = field_type
        # Key fields are always nullable to allow uninformed key values on unsaved objects
        self.nullable = bool(is_key) or bool(nullable)
        self.is_key = bool(is_key)
        self.related_model = related_model
        self.name: str = ''

    def get_value(self, v: Any) -> Any:
        """
        Return properly typed value. Raises error in case of receiving None for a non nullable field.
        If type requires a different logic to cast the value, that Field subclass should redefine this method.
        """
        if v is None:
            if self.nullable:
                return v
            else:
                raise ValueError(f"'{self.name}' field is not nullable")

        try:
            return self.field_type(v)
        except Exception as e:
            raise ModelField.InvalidValue(
                f"Error when converting value to {self.field_type.__name__} type for field '{self.name}': {str(e)}"
            )

    def get_related_model_field_type(self, model: 'ModelType') -> 'Model':
        """
        Method that returns the related_model class

        :param model: receives the field's parent model
        :return: the related_model class
        """

        field_type = self.related_model
        if not field_type:
            raise ModelField.NoRelatedModel(f"{model.__name__}'s field '{self.name}' has no related_model defined")

        if isinstance(self.related_model, str):
            if self.related_model == 'self':
                field_type = model
            else:
                # TODO register all defined Models to allow lazy reference through str with class' name
                raise NotImplementedError(
                    'Lazy Model reference for related_model not yet implemented, should use model\'s class '
                    'instead of str'
                )

        return field_type

    class InvalidValue(ModelException):
        """Custom exception to signal that the provided value is invalid for the field"""
        pass

    class WrongFieldType(ModelException):
        """Custom exception to signal that the defined type for the field is invalid"""
        pass

    class NoRelatedModel(ModelException):
        """Custom exception to signal that the field has no related_model attribute defined, when trying to use one"""
        pass


class StringField(ModelField):
    """Subclass of ModelField for string fields"""
    def __init__(self, nullable: bool = False, is_key: bool = False, related_model: RelatedModel = None,
                 max_length: int = None):
        super().__init__(field_type=str, nullable=nullable, is_key=is_key, related_model=related_model)
        self._max_length = max_length if max_length and max_length > 0 else None

    def get_value(self, v: Optional[str]) -> Any:
        v = super().get_value(v)
        if v is not None and self._max_length and len(v) > self._max_length:
            raise ModelField.InvalidValue(f"Value exceeded max_length of {self._max_length}, for field '{self.name}'")

        return v


class IntegerField(ModelField):
    """Subclass of ModelField for integer fields"""
    def __init__(self, nullable: bool = False, is_key: bool = False, related_model: RelatedModel = None):
        super().__init__(field_type=int, nullable=nullable, is_key=is_key, related_model=related_model)


class RelatedModelField(ModelField):
    """Subclass of ModelField for fields with a related_model. It can define any type, but it's int by default"""
    def __init__(self, related_model: RelatedModel, field_type: type = int, nullable: bool = False,
                 is_key: bool = False):
        """

        :param related_model: defines the field as a key of another model to establish a relationship
        :param field_type: type of the field, it should match that of the related_model's key. It default to int
        :param nullable: defines is field can be of value None for the Model
        :param is_key: defines if a field is the key field within its model
        """
        super().__init__(field_type=field_type, nullable=nullable, is_key=is_key, related_model=related_model)
