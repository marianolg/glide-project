from data_access import InMemoryJsonFileDataAccessor

config_test = {
    'SECRET_KEY': 'test',
    'STATIC_DATA_PATH': 'tests/tests_static_data',
    # Config an InMemoryJsonFileDataAccessor to avoid relying on external API data and API availability to execute tests
    'EMPLOYEES_DATA_ACCESSOR': InMemoryJsonFileDataAccessor('./tests/tests_static_data/employees.json'),
}
