from flask import Flask, send_from_directory
from api.routes import api_bp
from api.monitor import monitor_bp  

def create_app():
    app = Flask(__name__)

    # Register Blueprints for API and Monitoring
    app.register_blueprint(api_bp, url_prefix='/api')
    app.register_blueprint(monitor_bp, url_prefix='/monitor')

    # Configure logging
    import logging
    logging.basicConfig(level=logging.DEBUG)

    # Route for the index page (VM Provisioning Page)
    @app.route('/')
    def index():
        return send_from_directory('static', 'index.html')

    # Route for the monitor page (VM Monitoring Page)
    @app.route('/monitor')
    def monitor():
        return send_from_directory('static', 'monitor.html')

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, host='0.0.0.0')
