"Initializes the Flask application"
import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_caching import Cache
from mason_builder import MasonBuilder
# from Lovelace ->
# https://lovelace.oulu.fi/ohjelmoitava-web/ohjelmoitava-web/flask-api-project-layout/
# and github ->
# https://github.com/enkwolf/pwp-course-sensorhub-api-example/blob/master/sensorhub/__init__.py


db = SQLAlchemy()
cache = Cache()

# Based on http://flask.pocoo.org/docs/1.0/tutorial/factory/#the-application-factory
# Modified to use Flask SQLAlchemy
def create_app(test_config=None):
    "Create and configure an instance of the Flask application"
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY="dev",
        SQLALCHEMY_DATABASE_URI="sqlite:///" + os.path.join(app.instance_path,"task_management.db"),
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
        CACHE_TYPE="FileSystemCache",
        CACHE_DIR=os.path.join(app.instance_path, "cache"),

    )

    if test_config is None:
        app.config.from_pyfile("config.py", silent=True)
    else:
        app.config.from_mapping(test_config)

    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    db.init_app(app)
    cache.init_app(app)

    from . import models
    from . import api
    app.cli.add_command(models.init_db_command)
    app.register_blueprint(api.api_bp)

    return app
