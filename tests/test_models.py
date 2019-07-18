from pytest import raises
from flaskr import create_app
from models import Model, ModelField
from tests.utils import sorted_by_id
from tests.config_test import config_test

app = create_app(config_test)
with app.app_context():
    from flaskr.employees import Office, Department, Employee

    def test_get_all_offices_total_count():
        """Test getting correct count of all objects for a model using InMemoryJsonFileDataAccessor"""
        assert len(Office.get()) == 5

    def test_get_office_by_key():
        """Test getting correct specific object by key for a model using InMemoryJsonFileDataAccessor"""
        assert Office.get_by_key(1).to_dict() == {
            'id': 1,
            'city': 'San Francisco',
            'country': 'United States',
            'address': '450 Market St',
        }
    
    def test_get_offices_by_keys():
        """Test getting correct specific objects by keys for a model using InMemoryJsonFileDataAccessor"""
        assert sorted_by_id([o.to_dict() for o in Office.get_by_keys(2, 3)]) == sorted_by_id([{
            'id': 2,
            'city': 'New York',
            'country': 'United States',
            'address': '20 W 34th St',
        }, {
            'id': 3,
            'city': 'London',
            'country': 'United Kingdom',
            'address': '32 London Bridge St',
        }])

    def test_get_offices_with_limit_and_offset():
        """
        Test getting correct specific objects from list with limit  and offset values for a model using
        InMemoryJsonFileDataAccessor
        """
        assert sorted_by_id([o.to_dict() for o in Office.get(limit=2, offset=2)]) == sorted_by_id([{
            'id': 3,
            'city': 'London',
            'country': 'United Kingdom',
            'address': '32 London Bridge St',
        }, {
            'id': 4,
            'city': 'Chicago',
            'country': 'United States',
            'address': '233 S Wacker Dr',
        }])

    def test_get_employees_with_related_models():
        """Test getting specific objects of a model including data for several valid relationships"""
        assert sorted_by_id([e.to_dict() for e in Employee.get_by_keys(10, 11, with_related=[
            'manager.department.superdepartment',
            'manager.office',
            'department.superdepartment',
            'office',
        ])]) == sorted_by_id([{
            'id': 10,
            'first': 'Stephen',
            'last': 'Roberts',
            'manager': {
                'id': 4,
                'first': 'Ruth',
                'last': 'Morgan',
                'manager': None,
                'department': {
                    'id': 6,
                    'name': 'Outbound Sales',
                    'superdepartment': {'id': 1, 'name': 'Sales', 'superdepartment': None},
                },
                'office': {'id': 2, 'city': 'New York', 'country': 'United States', 'address': '20 W 34th St'},
            },
            'department': {
                'id': 6, 'name': 'Outbound Sales',
                'superdepartment': {'id': 1, 'name': 'Sales', 'superdepartment': None},
            },
            'office': {'id': 4, 'city': 'Chicago', 'country': 'United States', 'address': '233 S Wacker Dr'},
        }, {
            'id': 11,
            'first': 'Arthur',
            'last': 'Reed',
            'manager': {
                'id': 1,
                'first': 'Patricia',
                'last': 'Diaz',
                'manager': None,
                'department': {
                    'id': 5,
                    'name': 'Inbound Sales',
                    'superdepartment': {'id': 1, 'name': 'Sales', 'superdepartment': None},
                },
                'office': {'id': 2, 'city': 'New York', 'country': 'United States', 'address': '20 W 34th St'},
            },
            'department': {
                'id': 10, 'name': 'Product Management',
                'superdepartment': {'id': 3, 'name': 'Product', 'superdepartment': None},
            },
            'office': {'id': 4, 'city': 'Chicago', 'country': 'United States', 'address': '233 S Wacker Dr'},
        }])

    def test_get_department_add_related():
        """Test getting specific object and use its get_related method to get data for several valid related objects"""
        dep = Department.get_by_key(5)
        dep_with_superdepartment_detail = dep.get_related('superdepartment')
        dep_result = {
            'id': 5,
            'name': 'Inbound Sales',
            'superdepartment': 1
        }
        assert dep.to_dict() == dep_result
        assert dep_with_superdepartment_detail.to_dict() == {
            **dep_result,
            'superdepartment': {
                'id': 1,
                'name': 'Sales',
                'superdepartment': None,
            },
        }

    def test_get_employee_with_undefined_related_model():
        """Including an undefined field as related should raise a Model.UndefinedField exception"""
        with raises(Model.UndefinedField):
            Employee.get(with_related=['undefined_related_model'])

    def test_get_employee_with_related_model_using_field_with_no_related_model():
        """Including an valid field as that has no related_model should raise a ModelField.NoRelatedModel exception"""
        with raises(ModelField.NoRelatedModel):
            Employee.get(with_related=['first'])

    def test_get_related_data_for_different_model_types_fails():
        """
        Including different types of objects that differ the Model class calling get_related_models should result
        on a Model.IncorrectModelType exception
        """
        with raises(Model.IncorrectModelType):
            Employee.get_related_models([
                Employee(first='test', last='test'),
                Office(city='test', country='test', address='test'),
            ], 'manager')
