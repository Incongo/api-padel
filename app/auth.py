from flask import Blueprint, request
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity

from .extensions import db
from .models import Usuario

auth_bp = Blueprint("auth", __name__)

@auth_bp.post("/register")
def register():
    data = request.get_json() or {}
    nombre = (data.get("nombre") or "").strip()
    email = (data.get("email") or "").strip().lower()
    dni = (data.get("dni") or "").strip()
    password = data.get("password") or ""

    if not email or not password or not nombre or not dni:
        return {"error": "todos los campos son obligatorios"}, 400

    if Usuario.query.filter_by(email=email).first():
        return {"error": "email ya existe"}, 409

    user = Usuario(nombre=nombre, email=email, password=generate_password_hash(password), dni=dni, rol_id=2)
    db.session.add(user)
    db.session.commit()
    return {"id": user.id, "email": user.email}, 201

@auth_bp.post("/login")
def login():
    data = request.get_json() or {}
    email = (data.get("email") or "").strip().lower()
    password = data.get("password") or ""

    user = Usuario.query.filter_by(email=email).first()
    if not user or not check_password_hash(user.password, password):
        return {"error": "credenciales inválidas"}, 401

    # identity como string para JWT
    token = create_access_token(identity=str(user.id))  # :contentReference[oaicite:7]{index=7}
    return {"access_token": token}, 200

@auth_bp.post("/delete")

def delete_account():
    data = request.get_json() or {}
    user_id = data.get("user_id")
    # borrar usuario
    user = Usuario.query.get_or_404(user_id)
    db.session.delete(user)
    db.session.commit()
    return {"message": "cuenta eliminada"}, 200

@auth_bp.get("/me")
@jwt_required()
def me():
    user_id = int(get_jwt_identity())
    user = Usuario.query.get_or_404(user_id)
    return {"id": user.id, "email": user.email, "nombre": user.nombre, "dni": user.dni}