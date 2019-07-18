Glide Project
-------------

Service to access the company's employees's information.

RESTful API built with python and Flask.

**Configuration**

| Key               | Description                                                                  | Required     | Default       |
| ------------------| ---------------------------------------------------------------------------- | ----------   | ------------- |
| FLASK_APP         | Name of package containing Flask App. If informed, Should always be 'flaskr' | For DEV only | -             |
| FLASK_ENV         | Environment. Can be production, test, dev                                    | No           | production    |
| FLASK_DEBUG       | Enables Falsk Debug (0 disabled, 1 enabled). Should be disabled for PROD     | No           | 0             |
| SECRET_KEY        | API's Secret Key                                                             | No           | dev           |
| EMPLOYEES_API_URL | URLs to employees external API                                               | Yes          | -             |

**Run project**

 - *Using docker*

    1. Build image
        > docker build . glide-projec 

    2. Run at port XXXX (change XXXX for actual port)
        > docker run --env-file prod.env -d -p XXXX:5000 glide-project

    3. Run with dev config at port XXXX (change XXXX for actual port)
        > docker run --env-file dev.env -d -p XXXX:5000 --env startcmd="flask run --host 0.0.0.0 -p 5000" glide-project

---

 - *Without docker*
    1. Create python3.7 virtualenv (replace /path/to/venv for actual venv path)
        > python3.7 -m venv /path/to/venv

    2. Activate venv
        > source /path/to/venv/bin/activate

    3. Go to project dir (change /path/to/project for actual project root dir)
        > cd /path/to/project

    4. Upgrade pip
        > pip install --upgrade pip

    5. Install dependencies
        > pip install -r ./requirements.txt

    6. Run at port XXXX (change XXXX for actual port)
        > echo $(echo $(cat prod.env) gunicorn --bind 0.0.0.0:XXXX -w 1 wsgi:app) | bash

    7. Run with dev config at port XXXX (change XXXX for actual port)
        > echo $(echo $(cat dev.env) flask run --host 0.0.0.0 -p XXXX) | bash

    8. Deactivate venv
        > deactivate
