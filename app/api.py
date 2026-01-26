from flask import Blueprint, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime
from .extensions import db
from .models import Pista, Horario, Extra, Reserva, HorarioReserva, Usuario
from .permissions import user_required, owner_or_admin

# Blueprint principal del API (reservas y disponibilidad)
api_bp = Blueprint("api", __name__)


# =========================================================
# ===============   HELPERS INTERNOS   ====================
# =========================================================

def _user_id() -> int:
    """
    Devuelve el ID del usuario autenticado desde el JWT.
    Se usa en endpoints donde el usuario debe estar logueado.
    """
    return int(get_jwt_identity())


# =========================================================
# ===============   RESERVAS (USUARIO)   ==================
# =========================================================

@api_bp.post("/reservas")
@user_required
def crear_reserva():
    """
    Crear una reserva nueva.
    Reglas:
    - Debe incluir pista_id, fecha y lista de horarios.
    - No se puede reservar una franja ya ocupada.
    - Cada franja se guarda con el precio_base de la pista.
    - Si es fin de semana, se suma el extra 'fin de semana'.
    """
    data = request.get_json() or {}

    usuario_id = _user_id()
    pista_id = data.get("pista_id")
    fecha_str = data.get("fecha")
    horarios = data.get("horarios")

    # Validación básica
    if not pista_id or not fecha_str or not horarios:
        return {"error": "pista_id, fecha y horarios son obligatorios"}, 400

    # Convertir fecha string → date
    try:
        fecha = datetime.strptime(fecha_str, "%Y-%m-%d").date()
    except ValueError:
        return {"error": "Formato de fecha inválido. Usa YYYY-MM-DD"}, 400

    if not isinstance(horarios, list) or len(horarios) == 0:
        return {"error": "Debe incluir al menos una franja horaria"}, 400

    # Validar pista
    pista = Pista.query.get(pista_id)
    if not pista:
        return {"error": "Pista no encontrada"}, 404

    # Validar disponibilidad
    for h_id in horarios:
        existe = (
            db.session.query(HorarioReserva)
            .join(Reserva)
            .filter(
                Reserva.pista_id == pista_id,
                Reserva.fecha == fecha,
                HorarioReserva.horario_id == h_id,
            )
            .first()
        )
        if existe:
            return {
                "error": f"La franja {h_id} ya está reservada para esa pista y fecha"
            }, 409

    # -------------------------
    # CALCULAR PRECIO FINAL
    # -------------------------
    precio_final = pista.precio_base

    # Si es sábado (5) o domingo (6)
    if fecha.weekday() in (5, 6):
        extra_finde = Extra.query.filter_by(nombre="Fin de semana").first()
        if extra_finde:
            precio_final = precio_final + extra_finde.precio_extra

    # Crear reserva
    reserva = Reserva(
        usuario_id=usuario_id,
        pista_id=pista_id,
        fecha=fecha,
    )
    db.session.add(reserva)
    db.session.flush()

    # Crear horarios_reserva con precio final
    for h_id in horarios:
        hr = HorarioReserva(
            reserva_id=reserva.id,
            horario_id=h_id,
            precio=precio_final,
        )
        db.session.add(hr)

    db.session.commit()

    return {
        "id": reserva.id,
        "usuario_id": reserva.usuario_id,
        "pista_id": reserva.pista_id,
        "fecha": reserva.fecha.isoformat(),
        "horarios": horarios,
        "precio_final_por_franja": str(precio_final),
    }, 201



@api_bp.get("/reservas/mias")
@user_required
def mis_reservas():
    """
    Devuelve todas las reservas del usuario autenticado.
    Incluye el precio total (suma de precios por franja).
    """
    uid = _user_id()
    reservas = Reserva.query.filter_by(usuario_id=uid).all()

    return [
        {
            "id": r.id,
            "fecha": r.fecha.isoformat(),
            "pista": r.pista.nombre,
            "horarios": [hr.horario.franja for hr in r.horarios],
            "precio_total": str(sum(hr.precio for hr in r.horarios)),
        }
        for r in reservas
    ]

@api_bp.get("/reservas/<int:reserva_id>")
@owner_or_admin(allow_admin_edit=False)
def detalle_reserva(reserva_id):
    """
    Devuelve el detalle completo de una reserva.
    Incluye precio total.
    - El usuario solo puede ver sus reservas.
    - El admin puede ver todas, pero NO modificarlas.
    """
    r = Reserva.query.get_or_404(reserva_id)

    return {
        "id": r.id,
        "usuario": r.usuario.nombre,
        "pista": r.pista.nombre,
        "fecha": r.fecha.isoformat(),
        "horarios": [
            {
                "id": hr.horario.id,
                "franja": hr.horario.franja,
                "turno": hr.horario.turno,
                "precio": str(hr.precio),
            }
            for hr in r.horarios
        ],
        "precio_total": str(sum(hr.precio for hr in r.horarios)),
    }



@api_bp.delete("/reservas/<int:reserva_id>")
@owner_or_admin(allow_admin_edit=False)
def cancelar_reserva(reserva_id):
    """
    Cancela una reserva.
    - Solo el dueño puede cancelarla.
    - El admin NO puede cancelar reservas de usuarios.
    """
    r = Reserva.query.get_or_404(reserva_id)
    db.session.delete(r)
    db.session.commit()
    return {}, 204


# =========================================================
# ===============   DISPONIBILIDAD   =======================
# =========================================================

@api_bp.get("/disponibilidad")
def disponibilidad():
    """
    Devuelve las franjas horarias libres para una pista en una fecha.
    Parámetros:
    - pista_id
    - fecha
    """
    pista_id = request.args.get("pista_id")
    fecha = request.args.get("fecha")

    if not pista_id or not fecha:
        return {"error": "pista_id y fecha son obligatorios"}, 400

    # Todas las franjas existentes
    horarios = Horario.query.all()

    # Franjas ocupadas en esa pista y fecha
    ocupadas = (
        db.session.query(HorarioReserva.horario_id)
        .join(Reserva)
        .filter(
            Reserva.pista_id == pista_id,
            Reserva.fecha == fecha,
        )
        .all()
    )
    ocupadas = {h[0] for h in ocupadas}

    # Filtrar franjas libres
    libres = [
        {"id": h.id, "franja": h.franja, "turno": h.turno}
        for h in horarios
        if h.id not in ocupadas
    ]

    return {"libres": libres}
