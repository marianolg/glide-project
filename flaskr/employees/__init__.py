from flask import Blueprint
from .models import *
from .views import *

# Blueprint for employees module
blueprint = Blueprint('employees', __name__, url_prefix='/')

# Offices endpoints
blueprint.add_url_rule('/offices', 'list_offices', list_offices)
blueprint.add_url_rule('/offices/<int:key>', 'retrieve_office', retrieve_office)

# Departments endpoints
blueprint.add_url_rule('/departments', 'list_departments', list_departments)
blueprint.add_url_rule('/departments/<int:key>', 'retrieve_department', retrieve_department)

# Employees endpoints
blueprint.add_url_rule('/employees', 'list_employees', list_employees)
blueprint.add_url_rule('/employees/<int:key>', 'retrieve_employee', retrieve_employee)
