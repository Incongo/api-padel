from flask import Blueprint, request
from .extensions import db
from .models import Rol, Pista, Horario, Extra
from .permissions import admin_required

admin_bp = Blueprint("admin", __name__)

# -------------------------
# CRUD ROLES
# -------------------------
@admin_bp.get("/roles")
@admin_required
def list_roles():
    roles = Rol.query.order_by(Rol.id.asc()).all()
    return [{"id": r.id, "nombre": r.nombre} for r in roles]


@admin_bp.post("/roles")
@admin_required
def create_role():
    data = request.get_json() or {}
    nombre = (data.get("nombre") or "").strip()

    if not nombre:
        return {"error": "El nombre es obligatorio"}, 400

    if Rol.query.filter_by(nombre=nombre).first():
        return {"error": "El rol ya existe"}, 409

    r = Rol(nombre=nombre)
    db.session.add(r)
    db.session.commit()
    return {"id": r.id, "nombre": r.nombre}, 201


@admin_bp.patch("/roles/<int:role_id>")
@admin_required
def update_role(role_id):
    r = Rol.query.get_or_404(role_id)
    data = request.get_json() or {}

    if "nombre" in data:
        nombre = (data["nombre"] or "").strip()
        if not nombre:
            return {"error": "Nombre inválido"}, 400
        r.nombre = nombre

    db.session.commit()
    return {"id": r.id, "nombre": r.nombre}


@admin_bp.delete("/roles/<int:role_id>")
@admin_required
def delete_role(role_id):
    r = Rol.query.get_or_404(role_id)
    db.session.delete(r)
    db.session.commit()
    return {}, 204


# -------------------------
# CRUD PISTAS
# -------------------------
@admin_bp.get("/pistas")
@admin_required
def list_pistas():
    pistas = Pista.query.order_by(Pista.id.asc()).all()
    return [
        {
            "id": p.id,
            "nombre": p.nombre,
            "cubierta": p.cubierta,
            "plazas": p.plazas,
            "precio_base": str(p.precio_base),
        }
        for p in pistas
    ]


@admin_bp.post("/pistas")
@admin_required
def create_pista():
    data = request.get_json() or {}

    nombre = (data.get("nombre") or "").strip()
    cubierta = bool(data.get("cubierta", False))
    plazas = data.get("plazas")
    precio_base = data.get("precio_base")

    if not nombre or plazas is None or precio_base is None:
        return {"error": "nombre, plazas y precio_base son obligatorios"}, 400

    if Pista.query.filter_by(nombre=nombre).first():
        return {"error": "La pista ya existe"}, 409

    p = Pista(
        nombre=nombre,
        cubierta=cubierta,
        plazas=int(plazas),
        precio_base=precio_base,
    )
    db.session.add(p)
    db.session.commit()

    return {"id": p.id, "nombre": p.nombre}, 201


@admin_bp.patch("/pistas/<int:pista_id>")
@admin_required
def update_pista(pista_id):
    p = Pista.query.get_or_404(pista_id)
    data = request.get_json() or {}

    if "nombre" in data:
        p.nombre = (data["nombre"] or "").strip()
    if "cubierta" in data:
        p.cubierta = bool(data["cubierta"])
    if "plazas" in data:
        p.plazas = int(data["plazas"])
    if "precio_base" in data:
        p.precio_base = data["precio_base"]

    db.session.commit()
    return {"id": p.id, "nombre": p.nombre}


@admin_bp.delete("/pistas/<int:pista_id>")
@admin_required
def delete_pista(pista_id):
    p = Pista.query.get_or_404(pista_id)
    db.session.delete(p)
    db.session.commit()
    return {}, 204


# -------------------------
# CRUD HORARIOS
# -------------------------
@admin_bp.get("/horarios")
@admin_required
def list_horarios():
    horarios = Horario.query.order_by(Horario.id.asc()).all()
    return [
        {"id": h.id, "franja": h.franja, "turno": h.turno}
        for h in horarios
    ]


@admin_bp.post("/horarios")
@admin_required
def create_horario():
    data = request.get_json() or {}
    franja = (data.get("franja") or "").strip()
    turno = (data.get("turno") or "").strip()

    if not franja or not turno:
        return {"error": "franja y turno son obligatorios"}, 400

    if Horario.query.filter_by(franja=franja, turno=turno).first():
        return {"error": "El horario ya existe"}, 409

    h = Horario(franja=franja, turno=turno)
    db.session.add(h)
    db.session.commit()

    return {"id": h.id, "franja": h.franja, "turno": h.turno}, 201


@admin_bp.patch("/horarios/<int:horario_id>")
@admin_required
def update_horario(horario_id):
    h = Horario.query.get_or_404(horario_id)
    data = request.get_json() or {}

    if "franja" in data:
        h.franja = (data["franja"] or "").strip()
    if "turno" in data:
        h.turno = (data["turno"] or "").strip()

    db.session.commit()
    return {"id": h.id, "franja": h.franja, "turno": h.turno}


@admin_bp.delete("/horarios/<int:horario_id>")
@admin_required
def delete_horario(horario_id):
    h = Horario.query.get_or_404(horario_id)
    db.session.delete(h)
    db.session.commit()
    return {}, 204


# -------------------------
# CRUD EXTRAS
# -------------------------
@admin_bp.get("/extras")
@admin_required
def list_extras():
    extras = Extra.query.order_by(Extra.id.asc()).all()
    return [
        {"id": e.id, "nombre": e.nombre, "precio_extra": str(e.precio_extra)}
        for e in extras
    ]


@admin_bp.post("/extras")
@admin_required
def create_extra():
    data = request.get_json() or {}
    nombre = (data.get("nombre") or "").strip()
    precio_extra = data.get("precio_extra")

    if not nombre or precio_extra is None:
        return {"error": "nombre y precio_extra son obligatorios"}, 400

    if Extra.query.filter_by(nombre=nombre).first():
        return {"error": "El extra ya existe"}, 409

    e = Extra(nombre=nombre, precio_extra=precio_extra)
    db.session.add(e)
    db.session.commit()

    return {"id": e.id, "nombre": e.nombre}, 201


@admin_bp.patch("/extras/<int:extra_id>")
@admin_required
def update_extra(extra_id):
    e = Extra.query.get_or_404(extra_id)
    data = request.get_json() or {}

    if "nombre" in data:
        e.nombre = (data["nombre"] or "").strip()
    if "precio_extra" in data:
        e.precio_extra = data["precio_extra"]

    db.session.commit()
    return {"id": e.id, "nombre": e.nombre}


@admin_bp.delete("/extras/<int:extra_id>")
@admin_required
def delete_extra(extra_id):
    """
    Elimina un extra por ID.
    Solo el administrador puede hacerlo.
    """
    e = Extra.query.get_or_404(extra_id)
    db.session.delete(e)
    db.session.commit()
    return {}, 204

# -------------------------
# RESERVAS (ADMIN)
# -------------------------
from .models import Reserva, HorarioReserva, Usuario



@admin_bp.get("/reservas")
@admin_required
def admin_list_reservas():
    """
    Lista todas las reservas del sistema.
    Incluye precio total.
    El admin puede filtrar por:
    - fecha (YYYY-MM-DD)
    - pista_id
    - usuario_id
    """
    fecha = request.args.get("fecha")
    pista_id = request.args.get("pista_id")
    usuario_id = request.args.get("usuario_id")

    query = Reserva.query

    if fecha:
        query = query.filter(Reserva.fecha == fecha)
    if pista_id:
        query = query.filter(Reserva.pista_id == int(pista_id))
    if usuario_id:
        query = query.filter(Reserva.usuario_id == int(usuario_id))

    reservas = query.order_by(Reserva.fecha.asc()).all()

    return [
        {
            "id": r.id,
            "usuario": r.usuario.nombre,
            "usuario_id": r.usuario_id,
            "pista": r.pista.nombre,
            "pista_id": r.pista_id,
            "fecha": r.fecha.isoformat(),
            "horarios": [hr.horario.franja for hr in r.horarios],
            "precio_total": str(sum(hr.precio for hr in r.horarios)),
        }
        for r in reservas
    ]


@admin_bp.get("/reservas/<int:reserva_id>")
@admin_required
def admin_detalle_reserva(reserva_id):
    """
    Devuelve el detalle completo de una reserva.
    Incluye precio total.
    El admin puede ver cualquier reserva.
    NO puede modificarla ni cancelarla.
    """
    r = Reserva.query.get_or_404(reserva_id)

    return {
        "id": r.id,
        "usuario": {
            "id": r.usuario.id,
            "nombre": r.usuario.nombre,
            "email": r.usuario.email,
        },
        "pista": {
            "id": r.pista.id,
            "nombre": r.pista.nombre,
        },
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



