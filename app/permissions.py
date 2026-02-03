from functools import wraps
from flask import jsonify, request
from flask_jwt_extended import get_jwt_identity, jwt_required

from .models import Usuario, Reserva
from .extensions import db


# -----------------------------
# 1. Decorador: admin_required
# -----------------------------
def admin_required(fn):
    @wraps(fn)
    @jwt_required()
    def wrapper(*args, **kwargs):
        user_id = int(get_jwt_identity())
        user = Usuario.query.get(user_id)

        if not user or user.rol_id != 1:  # 1 = ADMIN
            return jsonify({"error": "Acceso restringido a administradores"}), 403

        return fn(*args, **kwargs)
    return wrapper


# -----------------------------
# 2. Decorador: user_required
# -----------------------------
def user_required(fn):
    @wraps(fn)
    @jwt_required()
    def wrapper(*args, **kwargs):
        user_id = int(get_jwt_identity())
        user = Usuario.query.get(user_id)

        if not user:
            return jsonify({"error": "Usuario no encontrado"}), 404

        return fn(*args, **kwargs)
    return wrapper


# ---------------------------------------------------------
# 3. Decorador: owner_or_admin (con reglas especiales)
# ---------------------------------------------------------
# - Admin puede VER reservas de todos
# - Admin NO puede modificar ni borrar reservas de usuarios
# - Usuario solo puede ver/modificar/borrar sus reservas
# ---------------------------------------------------------
def owner_or_admin(allow_admin_edit=False):
    """
    allow_admin_edit = False → admin solo puede VER, no modificar
    allow_admin_edit = True  → admin puede modificar (no lo usaremos en reservas)
    """

    def decorator(fn):
        @wraps(fn)
        @jwt_required()
        def wrapper(reserva_id, *args, **kwargs):
            user_id = int(get_jwt_identity())
            user = Usuario.query.get(user_id)
            reserva = Reserva.query.get_or_404(reserva_id)

            # Si es admin
            if user.rol_id == 1:
                if allow_admin_edit:
                    return fn(reserva_id, *args, **kwargs)
                else:
                    # Admin solo puede VER, no modificar
                    if request.method in ("GET",):
                        return fn(reserva_id, *args, **kwargs)
                    else:
                        return jsonify({"error": "El administrador no puede modificar reservas de usuarios"}), 403

            # Si es usuario normal → solo su reserva
            if reserva.usuario_id != user_id:
                return jsonify({"error": "No tienes permiso para acceder a esta reserva"}), 403

            return fn(reserva_id, *args, **kwargs)

        return wrapper
    return decorator
