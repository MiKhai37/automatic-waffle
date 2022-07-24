import logging
import os

from flask import Flask
from flask_cors import CORS


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)

    app.config.from_mapping(
        SECRET_KEY='very_not_secret_key',
    )

    if test_config is None:
        env_config = os.getenv("APP_SETTINGS", "config.DevelopmentConfig")
        app.config.from_object(env_config)
    else:
        # load the test config if passed in
        default_config = "config.Config"
        app.config.from_object(default_config)
        app.config.from_mapping(test_config)


    gunicorn_logger = logging.getLogger('gunicorn.error')
    app.logger.handlers = gunicorn_logger.handlers
    app.logger.setLevel(logging.DEBUG)
    app.logger.debug('App Initialization')

    db_name = app.config.get("DB_NAME")
    app.logger.info(f'DATABASE NAME: {db_name}')

    @app.route("/hello")
    def hello():
        return "This is Automatic Waffle, the backend of a scrabble app"

    # Link with mongo db
    from scrabble_flask import db
    db.link_app(app)
    # Blueprint registrations
    from scrabble_flask.routes import game, play, player
    
    app.register_blueprint(player.bp)
    app.register_blueprint(game.bp)
    app.register_blueprint(play.bp)

    # CORS
    CORS(app, supports_credentials=True)

    return app
