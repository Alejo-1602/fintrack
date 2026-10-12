"""
==============================================================================
FinTrack - Sistema de Control de Gastos Personales
==============================================================================
Autor: Alejandro Gonzalez
Curso: Sistemas Transaccionales
Docente: Jannez Milson Urrego Quiroz

Backend desarrollado en Python con Flask y PyMongo conectado a MongoDB Atlas.
Cumple con todos los Requisitos Funcionales (RQF-01 al RQF-13) y No Funcionales.
"""

import os
from datetime import datetime
from functools import wraps
from flask import (
    Flask,
    render_template,
    request,
    redirect,
    url_for,
    flash,
    session,
    Response
)
from pymongo import MongoClient, DESCENDING
from pymongo.errors import ConnectionFailure, PyMongoError
from bson.objectid import ObjectId
from bson import json_util
from werkzeug.security import generate_password_hash, check_password_hash
from dotenv import load_dotenv

# Cargar variables de entorno desde el archivo .env (si existe)
load_dotenv()

# Inicialización de la aplicación Flask
app = Flask(__name__)

# Configuración de clave secreta para el manejo seguro de sesiones criptográficas
app.secret_key = os.environ.get("SECRET_KEY", "fintrack_secreto_desarrollo_local_2026")

# Conexión a la base de datos MongoDB Atlas (o local por fallback)
MONGO_URI = os.environ.get(
    "MONGO_URI",
    "mongodb+srv://usuario:password@cluster.mongodb.net/fintrack_db?retryWrites=true&w=majority"
)

# Inicializar cliente de MongoDB
try:
    mongo_client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
    db = mongo_client["fintrack_db"]
    # Colecciones principales
    usuarios_col = db["usuarios"]
    movimientos_col = db["movimientos"]
except Exception as error_conexion:
    print(f"[ADVERTENCIA] Error al conectar con MongoDB Atlas: {error_conexion}")
    db = None
    usuarios_col = None
    movimientos_col = None


# ==============================================================================
# DECORADORES Y UTILIDADES DE AUTENTICACIÓN
# ==============================================================================

def login_required(f):
    """
    Decorador para proteger rutas privadas.
    Verifica manualmente la sesión de Flask sin requerir Flask-Login.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "usuario_id" not in session:
            flash("Debes iniciar sesión para acceder a esta sección.", "warning")
            return redirect(url_for("login"))
        return f(*args, **kwargs)
    return decorated_function


def verificar_conexion_bd():
    """
    Helper para verificar el estado de la base de datos antes de consultar.
    """
    if db is None or usuarios_col is None or movimientos_col is None:
        return False
    return True


# ==============================================================================
# RUTAS DE AUTENTICACIÓN Y SESIÓN (RQF-01, RQF-02, RQF-03)
# ==============================================================================

@app.route("/")
def index():
    """Ruta raíz: redirige al dashboard si ya hay sesión, o al login."""
    if "usuario_id" in session:
        return redirect(url_for("dashboard"))
    return redirect(url_for("login"))


@app.route("/registro", methods=["GET", "POST"])
def registro():
    """
    RQF-01: Registro de nuevo usuario.
    Solicita nombre, correo electrónico único y contraseña con hash seguro.
    """
    # Si el usuario ya está autenticado, enviarlo al dashboard
    if "usuario_id" in session:
        return redirect(url_for("dashboard"))

    if request.method == "POST":
        if not verificar_conexion_bd():
            flash("Error de conexión a la base de datos. Revisa la variable MONGO_URI.", "danger")
            return render_template("registro.html")

        nombre = request.form.get("nombre", "").strip()
        correo = request.form.get("correo", "").strip().lower()
        contrasena = request.form.get("contrasena", "")
        confirmar = request.form.get("confirmar_contrasena", "")

        # Validaciones de entrada (RQF-13)
        if not nombre or not correo or not contrasena:
            flash("Por favor, completa todos los campos obligatorios.", "warning")
            return render_template("registro.html")

        if len(contrasena) < 6:
            flash("La contraseña debe tener al menos 6 caracteres.", "warning")
            return render_template("registro.html")

        if contrasena != confirmar:
            flash("Las contraseñas no coinciden. Inténtalo de nuevo.", "warning")
            return render_template("registro.html")

        try:
            # Validar unicidad del correo electrónico (RQF-01)
            usuario_existente = usuarios_col.find_one({"correo": correo})
            if usuario_existente:
                flash("Ya existe un usuario registrado con este correo electrónico.", "danger")
                return render_template("registro.html")

            # Hash seguro de la contraseña usando werkzeug (RQNF-03)
            password_hash = generate_password_hash(contrasena)
            fecha_hoy_iso = datetime.now().strftime("%Y-%m-%d")

            # Documento de usuario según el modelo especificado
            nuevo_usuario = {
                "nombre": nombre,
                "correo": correo,
                "contraseña": password_hash,
                "fecha_registro": fecha_hoy_iso
            }

            resultado = usuarios_col.insert_one(nuevo_usuario)

            # Iniciar sesión automáticamente tras el registro exitoso
            session["usuario_id"] = str(resultado.inserted_id)
            session["usuario_nombre"] = nombre
            session["usuario_correo"] = correo

            flash(f"¡Bienvenido a FinTrack, {nombre}! Tu cuenta ha sido creada exitosamente.", "success")
            return redirect(url_for("dashboard"))

        except PyMongoError as err:
            flash(f"Error al registrar usuario en la base de datos: {str(err)}", "danger")

    return render_template("registro.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    """
    RQF-02: Inicio de sesión de usuarios registrados.
    Verifica correo y contraseña cifrada. Muestra error amigable si falla.
    """
    if "usuario_id" in session:
        return redirect(url_for("dashboard"))

    if request.method == "POST":
        if not verificar_conexion_bd():
            flash("No hay conexión con la base de datos MongoDB Atlas. Revisa tu archivo .env.", "danger")
            return render_template("login.html")

        correo = request.form.get("correo", "").strip().lower()
        contrasena = request.form.get("contrasena", "")

        if not correo or not contrasena:
            flash("Ingresa tu correo y contraseña para continuar.", "warning")
            return render_template("login.html")

        try:
            usuario = usuarios_col.find_one({"correo": correo})

            # Validar existencia de usuario y coincidencia del hash
            if usuario and check_password_hash(usuario.get("contraseña", ""), contrasena):
                session["usuario_id"] = str(usuario["_id"])
                session["usuario_nombre"] = usuario.get("nombre", "Usuario")
                session["usuario_correo"] = usuario.get("correo", "")

                flash(f"Bienvenido de nuevo, {session['usuario_nombre']}.", "success")
                return redirect(url_for("dashboard"))
            else:
                flash("Credenciales incorrectas. Verifica tu correo y contraseña.", "danger")

        except PyMongoError as err:
            flash(f"Error de base de datos durante el inicio de sesión: {str(err)}", "danger")

    return render_template("login.html")


@app.route("/logout")
def logout():
    """
    RQF-03: Cierre de sesión seguro.
    Limpia la sesión y redirige a la vista de inicio de sesión.
    """
    session.clear()
    flash("Has cerrado sesión correctamente. ¡Hasta pronto!", "info")
    return redirect(url_for("login"))


# ==============================================================================
# RUTAS DE MOVIMIENTOS FINANCIEROS (CRUD, BÚSQUEDA Y FILTROS)
# ==============================================================================

@app.route("/dashboard")
@login_required
def dashboard():
    """
    RQF-06: Listar movimientos del usuario ordenados por fecha descendente.
    RQF-07: Calcular y mostrar saldo actual (total ingresos - total gastos).
    RQF-08: Buscar movimientos por descripción o categoría.
    RQF-09: Filtrar por tipo (ingreso/gasto), categoría y mes (YYYY-MM).
    RQF-12: Resumen mensual con ingresos, gastos y balance del período.
    """
    if not verificar_conexion_bd():
        flash("No se puede conectar a MongoDB Atlas. Verifica la variable MONGO_URI.", "danger")
        return render_template(
            "dashboard.html",
            movimientos=[],
            saldo_actual=0.0,
            total_ingresos_mes=0.0,
            total_gastos_mes=0.0,
            balance_mes=0.0,
            total_mov_ingresos=0,
            total_mov_gastos=0,
            busqueda_query="",
            tipo_filtro="",
            categoria_filtro="",
            mes_filtro=""
        )

    user_oid = ObjectId(session["usuario_id"])

    # 1. Parámetros de búsqueda y filtros desde la URL (query strings)
    busqueda_query = request.args.get("q", "").strip()
    tipo_filtro = request.args.get("tipo", "").strip()
    categoria_filtro = request.args.get("categoria", "").strip()
    mes_filtro = request.args.get("mes", "").strip()

    # 2. Construcción del filtro para MongoDB (RQNF-08: Integridad por usuario)
    filtro_mongo = {"usuario_id": user_oid}

    if tipo_filtro in ["ingreso", "gasto"]:
        filtro_mongo["tipo"] = tipo_filtro

    if categoria_filtro:
        filtro_mongo["categoria"] = categoria_filtro

    if mes_filtro:
        # Filtra fecha con expresión regular que comience por 'YYYY-MM'
        filtro_mongo["fecha"] = {"$regex": f"^{mes_filtro}"}

    if busqueda_query:
        # Búsqueda flexible en descripción o categoría (RQF-08)
        regex_busqueda = {"$regex": busqueda_query, "$options": "i"}
        filtro_mongo["$or"] = [
            {"descripcion": regex_busqueda},
            {"categoria": regex_busqueda}
        ]

    # 3. Consulta de movimientos con orden descendente por fecha (RQF-06)
    cursor_movimientos = movimientos_col.find(filtro_mongo).sort([
        ("fecha", DESCENDING),
        ("fecha_registro", DESCENDING)
    ])
    movimientos = list(cursor_movimientos)

    # 4. Cálculo del Saldo Actual Global (Histórico total del usuario - RQF-07)
    todos_movimientos = list(movimientos_col.find({"usuario_id": user_oid}))
    total_ingresos_global = sum(m.get("monto", 0.0) for m in todos_movimientos if m.get("tipo") == "ingreso")
    total_gastos_global = sum(m.get("monto", 0.0) for m in todos_movimientos if m.get("tipo") == "gasto")
    saldo_actual = round(total_ingresos_global - total_gastos_global, 2)

    # 5. Cálculo del Resumen Mensual (RQF-12)
    # Si el usuario seleccionó un mes específico en el filtro, usamos ese mes.
    # De lo contrario, usamos el mes calendario actual (YYYY-MM).
    mes_referencia = mes_filtro if mes_filtro else datetime.now().strftime("%Y-%m")

    movimientos_mes = [m for m in todos_movimientos if str(m.get("fecha", "")).startswith(mes_referencia)]
    total_ingresos_mes = sum(m.get("monto", 0.0) for m in movimientos_mes if m.get("tipo") == "ingreso")
    total_gastos_mes = sum(m.get("monto", 0.0) for m in movimientos_mes if m.get("tipo") == "gasto")
    balance_mes = round(total_ingresos_mes - total_gastos_mes, 2)

    total_mov_ingresos = sum(1 for m in movimientos_mes if m.get("tipo") == "ingreso")
    total_mov_gastos = sum(1 for m in movimientos_mes if m.get("tipo") == "gasto")

    return render_template(
        "dashboard.html",
        movimientos=movimientos,
        saldo_actual=saldo_actual,
        total_ingresos_mes=round(total_ingresos_mes, 2),
        total_gastos_mes=round(total_gastos_mes, 2),
        balance_mes=balance_mes,
        total_mov_ingresos=total_mov_ingresos,
        total_mov_gastos=total_mov_gastos,
        busqueda_query=busqueda_query,
        tipo_filtro=tipo_filtro,
        categoria_filtro=categoria_filtro,
        mes_filtro=mes_filtro
    )


@app.route("/movimiento/nuevo", methods=["GET", "POST"])
@login_required
def agregar_movimiento():
    """
    RQF-04: Registrar ingreso.
    RQF-05: Registrar gasto.
    RQF-13: Validación de formularios (monto positivo, campos requeridos).
    """
    if request.method == "POST":
        if not verificar_conexion_bd():
            flash("Error de conexión a la base de datos.", "danger")
            return redirect(url_for("dashboard"))

        tipo = request.form.get("tipo", "").strip().lower()
        monto_str = request.form.get("monto", "").strip()
        categoria = request.form.get("categoria", "").strip().lower()
        descripcion = request.form.get("descripcion", "").strip()
        fecha = request.form.get("fecha", "").strip()

        # Validaciones de integridad y tipos
        if tipo not in ["ingreso", "gasto"]:
            flash("Tipo de movimiento inválido.", "warning")
            return redirect(url_for("agregar_movimiento"))

        if not monto_str or not categoria or not descripcion or not fecha:
            flash("Todos los campos son obligatorios.", "warning")
            return redirect(url_for("agregar_movimiento"))

        try:
            monto = float(monto_str)
            if monto <= 0:
                flash("El monto debe ser un valor numérico positivo mayor a 0.", "warning")
                return redirect(url_for("agregar_movimiento"))
        except ValueError:
            flash("El monto ingresado no es un número válido.", "warning")
            return redirect(url_for("agregar_movimiento"))

        # Estructura del documento según especificación del modelo NoSQL
        nuevo_movimiento = {
            "usuario_id": ObjectId(session["usuario_id"]),
            "tipo": tipo,
            "monto": round(monto, 2),
            "categoria": categoria,
            "descripcion": descripcion,
            "fecha": fecha,
            "fecha_registro": datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
        }

        try:
            movimientos_col.insert_one(nuevo_movimiento)
            flash(f"¡{tipo.capitalize()} registrado exitosamente por ${monto:,.2f}!", "success")
            return redirect(url_for("dashboard"))
        except PyMongoError as err:
            flash(f"Error al guardar movimiento: {str(err)}", "danger")

    fecha_hoy = datetime.now().strftime("%Y-%m-%d")
    return render_template("agregar_movimiento.html", fecha_hoy=fecha_hoy)


@app.route("/movimiento/editar/<id>", methods=["GET", "POST"])
@login_required
def editar_movimiento(id):
    """
    RQF-10: Actualizar datos de un movimiento existente.
    Verifica que el movimiento pertenezca al usuario en sesión.
    """
    if not verificar_conexion_bd():
        flash("Error de conexión a la base de datos.", "danger")
        return redirect(url_for("dashboard"))

    try:
        mov_oid = ObjectId(id)
        user_oid = ObjectId(session["usuario_id"])
    except Exception:
        flash("Identificador de movimiento inválido.", "danger")
        return redirect(url_for("dashboard"))

    # Buscar el movimiento asegurando que pertenezca al usuario en sesión (RQNF-03)
    movimiento = movimientos_col.find_one({"_id": mov_oid, "usuario_id": user_oid})
    if not movimiento:
        flash("El movimiento no existe o no tienes permisos para editarlo.", "danger")
        return redirect(url_for("dashboard"))

    if request.method == "POST":
        tipo = request.form.get("tipo", "").strip().lower()
        monto_str = request.form.get("monto", "").strip()
        categoria = request.form.get("categoria", "").strip().lower()
        descripcion = request.form.get("descripcion", "").strip()
        fecha = request.form.get("fecha", "").strip()

        if tipo not in ["ingreso", "gasto"]:
            flash("Tipo de movimiento inválido.", "warning")
            return render_template("editar_movimiento.html", movimiento=movimiento)

        if not monto_str or not categoria or not descripcion or not fecha:
            flash("Todos los campos son obligatorios.", "warning")
            return render_template("editar_movimiento.html", movimiento=movimiento)

        try:
            monto = float(monto_str)
            if monto <= 0:
                flash("El monto debe ser mayor a 0.", "warning")
                return render_template("editar_movimiento.html", movimiento=movimiento)
        except ValueError:
            flash("Monto numérico no válido.", "warning")
            return render_template("editar_movimiento.html", movimiento=movimiento)

        try:
            movimientos_col.update_one(
                {"_id": mov_oid, "usuario_id": user_oid},
                {
                    "$set": {
                        "tipo": tipo,
                        "monto": round(monto, 2),
                        "categoria": categoria,
                        "descripcion": descripcion,
                        "fecha": fecha
                    }
                }
            )
            flash("Movimiento actualizado correctamente.", "success")
            return redirect(url_for("dashboard"))
        except PyMongoError as err:
            flash(f"Error al actualizar el movimiento: {str(err)}", "danger")

    return render_template("editar_movimiento.html", movimiento=movimiento)


@app.route("/movimiento/eliminar/<id>", methods=["POST"])
@login_required
def eliminar_movimiento(id):
    """
    RQF-11: Eliminar movimiento con verificación de pertenencia.
    RQNF-12: El saldo se actualiza automáticamente al recalcularse en el dashboard.
    """
    if not verificar_conexion_bd():
        flash("Error de conexión a la base de datos.", "danger")
        return redirect(url_for("dashboard"))

    try:
        mov_oid = ObjectId(id)
        user_oid = ObjectId(session["usuario_id"])

        resultado = movimientos_col.delete_one({"_id": mov_oid, "usuario_id": user_oid})
        if resultado.deleted_count > 0:
            flash("Movimiento eliminado correctamente.", "info")
        else:
            flash("No se encontró el movimiento a eliminar o no tienes permisos.", "warning")

    except Exception as err:
        flash(f"Error al eliminar el movimiento: {str(err)}", "danger")

    return redirect(url_for("dashboard"))


@app.route("/exportar-json")
@login_required
def exportar_datos():
    """
    RQNF-09: Respaldo de datos.
    Permite al usuario exportar todos sus movimientos en formato JSON para copia de seguridad.
    """
    if not verificar_conexion_bd():
        flash("Error al acceder a la base de datos.", "danger")
        return redirect(url_for("dashboard"))

    user_oid = ObjectId(session["usuario_id"])
    movimientos = list(movimientos_col.find({"usuario_id": user_oid}).sort("fecha", DESCENDING))

    # Convertir documentos BSON a JSON legible
    contenido_json = json_util.dumps(movimientos, indent=2)

    nombre_archivo = f"fintrack_respaldo_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    return Response(
        contenido_json,
        mimetype="application/json",
        headers={"Content-Disposition": f"attachment;filename={nombre_archivo}"}
    )


# ==============================================================================
# MANEJADORES DE ERRORES HTTP
# ==============================================================================

@app.errorhandler(404)
def error_404(e):
    return render_template(
        "base.html",
        content="""<div style='text-align:center;padding:4rem 1rem;'>
            <h1 style='font-size:3rem;color:#c0392b;'>404</h1>
            <h2>Página no encontrada</h2>
            <p>La ruta que buscas no existe en FinTrack.</p>
            <br><a href='/' class='btn btn-primary'>Volver al Inicio</a>
        </div>"""
    ), 404


@app.errorhandler(500)
def error_500(e):
    return render_template(
        "base.html",
        content="""<div style='text-align:center;padding:4rem 1rem;'>
            <h1 style='font-size:3rem;color:#c0392b;'>500</h1>
            <h2>Error interno del servidor</h2>
            <p>Ocurrió un problema procesando la solicitud.</p>
            <br><a href='/' class='btn btn-primary'>Volver al Inicio</a>
        </div>"""
    ), 500


# ==============================================================================
# PUNTO DE ENTRADA PRINCIPAL PARA EJECUCIÓN LOCAL
# ==============================================================================

if __name__ == "__main__":
    # Render asigna automáticamente el puerto a través de la variable PORT
    puerto = int(os.environ.get("PORT", 5000))
    # En desarrollo local activamos debug=True
    app.run(host="0.0.0.0", port=puerto, debug=True)
