# 💰 FinTrack - Sistema de Control de Gastos Personales

> **Proyecto:** Sistemas Transaccionales  
> **Autor:** Alejandro Gonzalez  
> **Docente:** Jannez Milson Urrego Quiroz  
> **Versión:** 1.0 (Noviembre 2026)

---

## 📌 1. Descripción General del Proyecto

**FinTrack** es una aplicación web transaccional diseñada para permitir a los usuarios gestionar sus finanzas personales de forma intuitiva, organizada y segura. Cada usuario cuenta con su propia cuenta privada para registrar ingresos y gastos clasificados por categoría, consultar en tiempo real su saldo disponible acumulado, buscar y filtrar transacciones por fechas o descripciones, y analizar su balance mensual.

La aplicación utiliza **MongoDB Atlas** como base de datos NoSQL en la nube, aprovechando la flexibilidad del modelo de documentos para almacenar transacciones financieras sin rigidez de esquema.

---

## 🚀 2. Stack Tecnológico

| Capa | Tecnología | Descripción |
| :--- | :--- | :--- |
| **Backend** | Python 3.10+ & Flask | Servidor web micro-framework con enrutamiento y lógica de negocio |
| **Base de Datos** | MongoDB Atlas (NoSQL) | Clúster en la nube con réplicas gestionadas |
| **Driver BD** | PyMongo & dnspython | Conector oficial nativo de Python para MongoDB |
| **Frontend** | HTML5, CSS3 puro, JS puro | Interfaz dinámica, responsive y estilizada (sin Bootstrap ni Tailwind) |
| **Motor de Vistas** | Jinja2 | Renderizado de plantillas dinámicas desde el backend |
| **Autenticación** | Sesiones de Flask + Werkzeug | Cifrado criptográfico de contraseñas con hash SHA-256 / scrypt |
| **Servidor Producción** | Gunicorn | WSGI HTTP Server para despliegue en producción |
| **Despliegue** | Render (Web Service) | Alojamiento en la nube con CI/CD automatizado desde GitHub |
| **Generador QR** | `qrcode[pil]` (Python) | Generación automática del código QR para acceso móvil |

---

## 📁 3. Estructura del Proyecto

```text
fintrack/
│
├── app.py                     # Servidor Flask principal y lógica transaccional
├── requirements.txt           # Dependencias de Python para producción y desarrollo
├── Procfile                   # Comando de inicio para servidores en la nube (Render)
├── runtime.txt                # Versión fijada de Python (python-3.11.6)
├── .env.example               # Plantilla de variables de entorno seguras
├── .env                       # Variables de entorno locales (ignorado por Git)
├── .gitignore                 # Exclusión de archivos sensibles y temporales
├── README.md                  # Documentación completa y manual de usuario
├── generar_qr.py              # Script generador del código QR de acceso móvil
├── static/
│   └── css/
│       └── style.css          # Estilos CSS3 puros con diseño moderno y responsive
└── templates/
    ├── base.html              # Plantilla maestra con navbar, alertas flash y pie
    ├── login.html             # Pantalla de inicio de sesión de usuario (RQF-02)
    ├── registro.html          # Pantalla de creación de cuenta nueva (RQF-01)
    ├── dashboard.html         # Panel principal: saldo, filtros y tabla (RQF-06..12)
    ├── agregar_movimiento.html# Formulario interactivo para ingresos/gastos (RQF-04/05)
    └── editar_movimiento.html # Formulario de modificación de movimientos (RQF-10)
```

---

## 📋 4. Requisitos del Sistema (Evidencia 4)

### Requisitos Funcionales (RQF)
- **RQF-01 (Registro de usuario):** Registro con nombre, correo electrónico único y contraseña cifrada.
- **RQF-02 (Inicio de sesión):** Acceso mediante correo y contraseña con validación de credenciales.
- **RQF-03 (Cierre de sesión):** Cierre seguro invalidando la sesión de Flask.
- **RQF-04 (Registrar ingreso):** Captura de monto, categoría (`salario`, `beca`, `regalo`, `otros`), fecha y descripción.
- **RQF-05 (Registrar gasto):** Captura de monto, categoría (`comida`, `transporte`, `estudio`, `ocio`, `servicios`, `otros`), fecha y descripción.
- **RQF-06 (Listar movimientos):** Visualización exclusiva de los registros del usuario autenticado ordenados cronológicamente descendente.
- **RQF-07 (Calcular saldo):** Saldo total acumulado = $\sum \text{Ingresos} - \sum \text{Gastos}$.
- **RQF-08 (Buscar movimientos):** Búsqueda insensible a mayúsculas/minúsculas por descripción o categoría.
- **RQF-09 (Filtrar movimientos):** Filtro multi-criterio por tipo (`ingreso`/`gasto`), categoría y mes (`YYYY-MM`).
- **RQF-10 (Actualizar movimiento):** Edición de monto, categoría, descripción y fecha con validación de pertenencia.
- **RQF-11 (Eliminar movimiento):** Eliminación de movimientos con confirmación previa.
- **RQF-12 (Resumen mensual):** Cálculo y visualización de ingresos del mes, gastos del mes y balance neto.
- **RQF-13 (Validación de formularios):** Validación de campos obligatorios y montos numéricos estrictamente positivos (> 0).

### Requisitos No Funcionales (RQNF)
- **RQNF-01 (Usabilidad):** Interfaz limpia, intuitiva y colores visuales estándar (verde `#27ae60` para ingresos, rojo `#c0392b` para gastos).
- **RQNF-02 (Rendimiento):** Respuesta rápida de consultas en menos de 3 segundos.
- **RQNF-03 (Seguridad):** Hash seguro con `generate_password_hash` y consultas filtradas por `usuario_id`.
- **RQNF-04 (Escalabilidad):** Base de datos NoSQL distribuida en MongoDB Atlas.
- **RQNF-08 (Integridad):** Relación de movimientos ligada a `ObjectId(usuario_id)` para prevenir registros huérfanos.
- **RQNF-09 (Respaldo):** Endpoint dedicado `/exportar-json` para descargar los datos en formato JSON.
- **RQNF-11 (Precisión):** Manejo financiero exacto redondeado a dos cifras decimales.

---

## 🗄️ 5. Modelo de Datos en MongoDB Atlas

Base de datos: `fintrack_db`

### Colección: `usuarios`
```json
{
  "_id": ObjectId("6709f123456789abcdef0001"),
  "nombre": "Alejandro Gonzalez",
  "correo": "alejandro@ejemplo.com",
  "contraseña": "scrypt:32768:8:1$hash_seguro_de_la_contraseña...",
  "fecha_registro": "2026-10-12"
}
```

### Colección: `movimientos`
```json
{
  "_id": ObjectId("6709f987654321fedcba0002"),
  "usuario_id": ObjectId("6709f123456789abcdef0001"),
  "tipo": "gasto",
  "monto": 25000.00,
  "categoria": "comida",
  "descripcion": "Almuerzo en la universidad",
  "fecha": "2026-10-12",
  "fecha_registro": "2026-10-12T14:30:00"
}
```

---

## 💻 6. Instalación y Ejecución Local

### Paso 1: Clonar o abrir la carpeta del proyecto
Abre una terminal en la carpeta `fintrack`:
```bash
cd fintrack
```

### Paso 2: Crear y activar un entorno virtual de Python
**En Windows (PowerShell):**
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

**En Linux / Mac:**
```bash
python3 -m venv venv
source venv/bin/activate
```

### Paso 3: Instalar dependencias
```bash
pip install -r requirements.txt
```

### Paso 4: Configurar variables de entorno
Crea tu archivo `.env` basado en `.env.example`:
```bash
cp .env.example .env
```
Edita `.env` e introduce tu cadena de conexión a MongoDB Atlas y una clave secreta:
```env
MONGO_URI=mongodb+srv://<usuario>:<password>@cluster0.xxxxx.mongodb.net/fintrack_db?retryWrites=true&w=majority
SECRET_KEY=clave_secreta_local_para_desarrollo
PORT=5000
```

### Paso 5: Iniciar la aplicación en modo desarrollo
```bash
python app.py
```
Abre tu navegador web en: **`http://localhost:5000`**

---

## 🌐 7. Guía Paso a Paso para Despliegue en la Nube

Sigue este checklist secuencial para dejar la aplicación 100% pública:

### Checklist A: Crear Base de Datos en MongoDB Atlas (Gratis)
1. Ingresa a [mongodb.com/cloud/atlas](https://www.mongodb.com/cloud/atlas) e inicia sesión o crea una cuenta gratuita.
2. Crea un clúster gratuito **M0 Free Tier** (proveedor AWS, región cercana ej. us-east-1).
3. En la sección **Security > Database Access**:
   - Crea un usuario de base de datos (ej. `admin_fintrack`) con contraseña segura. Recuerda no usar símbolos como `@` o `:` dentro de la contraseña para evitar problemas con la URL de conexión.
4. En la sección **Security > Network Access**:
   - Agrega una IP con acceso universal: `0.0.0.0/0` (Allow Access from Anywhere) para permitir que el servidor en Render pueda conectarse.
5. En la sección **Database > Clusters**, haz clic en **Connect > Drivers > Python (3.11 or later)**.
6. Copia tu cadena de conexión `MONGO_URI`. Tendrá un formato como:
   `mongodb+srv://admin_fintrack:<password>@cluster0.xxxxx.mongodb.net/fintrack_db?retryWrites=true&w=majority`
   *(Sustituye `<password>` por la contraseña real que creaste)*.

---

### Checklist B: Subir el Proyecto a GitHub
1. Abre tu terminal en la carpeta `fintrack`:
   ```bash
   git init
   git add .
   git commit -m "feat: versión inicial completa de FinTrack"
   ```
2. Crea un nuevo repositorio público o privado en [github.com](https://github.com) llamado `fintrack`.
3. Vincula el remoto y sube la rama principal:
   ```bash
   git branch -M main
   git remote add origin https://github.com/<tu-usuario>/fintrack.git
   git push -u origin main
   ```

---

### Checklist C: Desplegar en Render (Web Service Gratuito)
1. Ingresa a [render.com](https://render.com) e inicia sesión con tu cuenta de GitHub.
2. En el panel principal, haz clic en **New + > Web Service**.
3. Selecciona la opción **Build and deploy from a Git repository** y conecta tu repositorio `fintrack`.
4. Diligencia los siguientes campos de configuración:
   - **Name:** `fintrack-app` (o el nombre de tu preferencia)
   - **Region:** Ohio (US East) o Frankfurt
   - **Branch:** `main`
   - **Root Directory:** déjalo en blanco (o `fintrack` si subiste la carpeta contenedora completa)
   - **Runtime:** `Python 3`
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `gunicorn app:app`
   - **Instance Type:** `Free`
5. En la sección **Environment Variables**, añade las siguientes 2 variables:
   - `MONGO_URI`: Pega la cadena de conexión completa de MongoDB Atlas obtenida en el Checklist A.
   - `SECRET_KEY`: Una cadena aleatoria y segura para cifrar las cookies de sesión (ej: `super_clave_fintrack_prod_2026`).
6. Haz clic en **Create Web Service**.
7. Render iniciará la construcción (`build`) y el despliegue automático. En 2-3 minutos verás el estado en verde: **`Live`**.
8. Copia la URL pública generada (ej: `https://fintrack-app.onrender.com`).

---

### Checklist D: Generar el Código QR de Acceso Móvil
Tu aplicación ya se encuentra desplegada y accesible públicamente en la nube en:
👉 **https://fintrack-m7hs.onrender.com**

El código QR ya fue generado en la raíz del proyecto como:
**`fintrack_qr.png`**

Si deseas regenerarlo en cualquier momento, ejecuta:
```bash
python generar_qr.py https://fintrack-m7hs.onrender.com
```

¡Listo! Comparte o imprime esa imagen para que cualquier evaluador o usuario pueda acceder a FinTrack desde su dispositivo móvil al instante.
