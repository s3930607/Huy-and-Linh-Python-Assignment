from flask import Flask

from routes import level1, level2, level3


def create_app():
    app = Flask(__name__)
    app.register_blueprint(level1.bp)
    app.register_blueprint(level2.bp)
    app.register_blueprint(level3.bp)
    return app


if __name__ == "__main__":
    create_app().run(debug=True)
