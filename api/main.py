import os

from flask import Flask, jsonify
from flask_cors import CORS

import account
import feedback
import news
import restriction
import route_planner
import suggestions
import tools
import weather


def create_app() -> Flask:
    app = Flask(__name__)
    app.config["JSON_AS_ASCII"] = False
    app.json.ensure_ascii = False

    CORS(
        app,
        resources={r"/*": {"origins": "*"}},
        supports_credentials=True,
        allow_headers="*",
        methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    )

    for module in (weather, restriction, route_planner, suggestions, news, tools, account, feedback):
        app.register_blueprint(module.router.blueprint)

    @app.get("/")
    def read_root():
        return jsonify({"message": "Welcome to MotoTravel API"})

    @app.get("/docs")
    def docs_notice():
        return jsonify({
            "message": "MotoTravel API is running on Flask. FastAPI Swagger docs are no longer available."
        })

    return app


app = create_app()


if __name__ == "__main__":
    debug = os.getenv("FLASK_DEBUG") == "1"
    host = os.getenv("API_HOST", "0.0.0.0")
    port = int(os.getenv("API_PORT", "8000"))
    app.run(host=host, port=port, debug=debug, use_reloader=False)
