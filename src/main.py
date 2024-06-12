import os
import sys
import argparse

sys.path.append(os.path.dirname(__file__))

from __init__ import create_app
from routes.auth import auth_bp
from routes.closet import closet_bp
from routes.outfit import outfit_bp


def main(config_name="development"):
    app = create_app(config_name)
    app.register_blueprint(auth_bp)
    app.register_blueprint(closet_bp)
    app.register_blueprint(outfit_bp)

    app.run(host="0.0.0.0", port=app.config['PORT'], debug=app.config["DEBUG"])


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Run the Flask app.')
    parser.add_argument('--config', default='development', help='The configuration name to use (default: development)')
    args = parser.parse_args()

    main(config_name=args.config)