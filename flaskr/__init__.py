from flask import Flask


def create_app(test_config=None):
    app = Flask(__name__)
    app.config.from_mapping(
        SECRET_KEY='dev',  # SECRET_KEY To use in case is not defined at config.py. NOT SUITABLE FOR PRODUCTION ENV
    )

    if test_config is None:
        app.config.from_pyfile('config.py', silent=True)
    else:
        app.config.from_mapping(test_config)

    app.app_context().push()

    app.static_data_path = f'{app.root_path}/../{app.config["STATIC_DATA_PATH"]}'
    if not app.config.get('EMPLOYEES_API_URL') and not app.config.get('EMPLOYEES_DATA_ACCESSOR'):
        # If EMPLOYEES_API_URL is not set, and neither custom EMPLOYEES_DATA_ACCESSOR is defined, then throw error
        raise AttributeError('EMPLOYEES_API_URL or EMPLOYEES_DATA_ACCESSOR must be set.')

    from flaskr.employees import blueprint as employees_blueprint
    app.register_blueprint(employees_blueprint)

    return app


if __name__ == '__main__':
    create_app().run(debug=True, use_debugger=False, use_reloader=True, passthrough_errors=True)
