from flask import Flask, send_from_directory
from api.routes import api_bp


def create_app():
    app = Flask(__name__)

    # Register Blueprints
    app.register_blueprint(api_bp, url_prefix='/api')

    # Optional: configure logging
    import logging
    logging.basicConfig(level=logging.DEBUG)

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)
