from pytest import fixture
from flaskr import create_app
from flaskr.employees import Office, Department, Employee
from tests.config_test import config_test
from tests.utils import _test_retrieve_model, _test_retrieve_model_not_found, _test_list_model
import json


@fixture
def client():
    app = create_app(config_test)
    client = app.test_client()

    yield client


def test_retrieve_office(client):
    """
    Tests fetching a specific Office from /offices/key view, and compares the result to getting the same object
    directly through the model
    """

    key = 1
    _test_retrieve_model(client, f'/offices/{key}', Office, key)


def test_retrieve_office_not_found(client):
    """Tests fetching a specific Office from /offices/key, that should not be found"""
    _test_retrieve_model_not_found(client, f'/offices/99')


def test_retrieve_department(client):
    """
    Tests fetching a specific Department from /departments/key view, and compares the result to getting the same object
    directly through the model
    """

    key = 1
    _test_retrieve_model(client, f'/departments/{key}', Department, key)


def test_retrieve_department_not_found(client):
    """Tests fetching a specific Department from /departments/key, that should not be found"""
    _test_retrieve_model_not_found(client, f'/departments/99')


def test_retrieve_employee(client):
    """
    Tests fetching a specific Employee from /employees/key view, and compares the result to getting the same object
    directly through the model
    """

    key = 1
    _test_retrieve_model(client, f'/employees/{key}', Employee, key)


def test_list_offices(client):
    """
    Tests fetching all offices from /offices view, and compares the results to getting the same objects directly
    through the model
    """

    _test_list_model(client, '/offices', Office)


def test_list_departments(client):
    """
    Tests fetching all departments from /departments view, and compares the results to getting the same objects
    directly through the model
    """

    _test_list_model(client, '/departments', Department)


def test_list_employees(client):
    """
    Tests fetching all employees from /employees view, and compares the results to getting the same objects directly
    through the model
    """

    _test_list_model(client, '/employees', Employee, limit=100)


def test_list_employees_with_limit_offset(client):
    """
    Tests fetching some employees from /employees view, using limit and offset values, and compares the results to
    getting the same objects directly through the model
    """

    attrs = {'limit': 2, 'offset': 5}
    _test_list_model(client, f'/employees?limit={attrs["limit"]}&offset={attrs["offset"]}', Employee, **attrs)


def test_retrieve_department_expanding_related_models(client):
    """
    Tests fetching a department from /departments/key view, expanding on superdepartment.superdepartment related models
    """

    key = 10
    _test_retrieve_model(
        client,
        f'/departments/{key}?expand=superdepartment.superdepartment',
        Department,
        key,
        with_related=['superdepartment.superdepartment'],
    )


def test_list_employees_expanding_related_models(client):
    """
    Tests fetching employees with limit and offset values from /employees view, expanding on several valid relationships
    """

    attrs = {'limit': 2, 'offset': 5}
    related_models = [
        'manager.department.superdepartment',
        'manager.office',
        'department.superdepartment',
        'office',
    ]
    _test_list_model(
        client,
        f'/employees?limit={attrs["limit"]}&offset={attrs["offset"]}'
        f'&{"&".join([f"expand={rm}" for rm in related_models])}',
        Employee,
        **attrs,
        with_related=related_models,
    )


def test_retrieve_employee_with_invalid_related_model(client):
    """Tests for 400 error when fetching from /employees trying to expand on undefined field"""
    undefined_related_model = 'undefined_related_model'
    resp = client.get(f'/employees?expand={undefined_related_model}')
    assert resp.status_code == 400
    assert json.loads(resp.data)['error'] == f"Employee has no '{undefined_related_model}' field"


def test_retrieve_employee_with_invalid_related_model(client):
    """
    Tests for 400 error when fetching from /employees trying to expand on 'first' field, which has no related_model
    defined
    """
    no_related_model_field = 'first'
    resp = client.get(f'/employees?expand={no_related_model_field}')
    assert resp.status_code == 400
    assert json.loads(resp.data)['error'] == f"Employee's field '{no_related_model_field}' has no related_model defined"
