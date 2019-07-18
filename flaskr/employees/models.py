from flask import current_app as app
from models import Model, StringField, IntegerField, RelatedModelField
from data_access import InMemoryJsonFileDataAccessor, JsonRestApiDataAccessor
from typing import Union


class Office(Model):
    id = IntegerField(is_key=True)
    city = StringField()
    country = StringField()
    address = StringField()

    _data_accessor = InMemoryJsonFileDataAccessor(f'{app.static_data_path}/offices.json')

    def __init__(self, city: str, country: str, address: str, id: int = None):
        """Explicit __init__ override to expose creation signature for static checks"""
        super().__init__(id=id, city=city, country=country, address=address)


class Department(Model):
    id = IntegerField(is_key=True)
    name = StringField()
    superdepartment = RelatedModelField('self', nullable=True)

    _data_accessor = InMemoryJsonFileDataAccessor(f'{app.static_data_path}/departments.json')

    def __init__(self, name: str, superdepartment: Union[int, 'Department'] = None, id: int = None):
        """Explicit __init__ override to expose creation signature for static checks"""
        super().__init__(id=id, name=name, superdepartment=superdepartment)


class Employee(Model):
    id = IntegerField(is_key=True)
    first = StringField()
    last = StringField()
    manager = RelatedModelField('self', nullable=True)
    department = RelatedModelField(Department, nullable=True)
    office = RelatedModelField(Office, nullable=True)

    # Employee data accessor can be configured to plug in a mocked data source for testing purposes. If
    #  EMPLOYEES_DATA_ACCESSOR is not configured, actual JsonRestApiDataAccessor pointing to configured web API is used
    _data_accessor = app.config.get('EMPLOYEES_DATA_ACCESSOR') or \
        JsonRestApiDataAccessor(f'{app.config["EMPLOYEES_API_URL"]}/bigcorp/employees')

    def __init__(self, first: str, last: str, manager: Union[int, 'Employee'] = None,
                 department: Union[int, Department] = None, office: Union[int, Office] = None, id: int = None):
        """Explicit __init__ override to expose creation signature for static checks"""
        super().__init__(id=id, first=first, last=last, manager=manager, department=department, office=office)
