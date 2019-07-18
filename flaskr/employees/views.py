from views import list_view, retrieve_view
from .models import Office, Department, Employee
from flask import jsonify


def list_offices():
    return list_view(Office)


def retrieve_office(key: int):
    return retrieve_view(Office, key)


def list_departments():
    return list_view(Department)


def retrieve_department(key: int):
    return retrieve_view(Department, key)


def list_employees():
    return list_view(Employee)


def retrieve_employee(key: int):
    if key <= 0:
        return jsonify({'error': 'Key should be greater than 0'}), 400

    return retrieve_view(Employee, key)
