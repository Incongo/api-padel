from flask import Flask, request
from dotenv import load_dotenv
from flask_cors import CORS

from .config import Config
from .extensions import db, migrate, jwt

def create_app():
    load_dotenv()
    app = Flask(__name__)
    app.config.from_object(Config)

    CORS(app, resources={r"/*": {"origins": "*"}})

    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)

    # 🔹 Blueprint de autenticación
    from .auth import auth_bp
    app.register_blueprint(auth_bp, url_prefix="/auth")

    # 🔹 Blueprint principal del API (AÑADIR ESTO)
    from .api import api_bp
    app.register_blueprint(api_bp, url_prefix="/api")
    
    from .admin_routes import admin_bp
    app.register_blueprint(admin_bp, url_prefix="/admin")

    @app.route("/")
    def index():
        return {"message": "¡La aplicación está funcionando!"}

    return app
