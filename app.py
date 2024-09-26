from flask import Flask, render_template, redirect, url_for, request, flash
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from datetime import timedelta
from dotenv import load_dotenv
from database.sql_server_connection import SQLServerDatabase
import os

app = Flask(__name__)

# Cargar las variables de entorno desde .env
load_dotenv()
app.secret_key = os.getenv('SECRET_KEY', ',btqS$NE@+dr}^L&?<C6')  # Cambia esto por una clave secreta segura en producción
app.permanent_session_lifetime = timedelta(minutes=10)  # Tiempo máximo de inactividad antes de cerrar la sesión

# Instancia de conexión a la base de datos
db = SQLServerDatabase('SQL_SERVER', 'SQL_DATABASE', 'SQL_USERNAME', 'SQL_PASSWORD')

# Configuración de Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Simulación de usuarios (en un entorno real, usarías una base de datos para gestionar usuarios)
users = {
    'testuser': {'password': '123456', 'email': 'testuser@example.com', 'active': True},
    'user1': {'password': 'user1pass', 'email': 'user1@example.com', 'active': True},
    'user2': {'password': 'user2pass', 'email': 'user2@example.com', 'active': True}
}

# Modelo de usuario para Flask-Login
class User(UserMixin):
    def __init__(self, username):
        self.id = username

# Cargar usuario para Flask-Login
@login_manager.user_loader
def load_user(username):
    if username not in users:
        return None
    user_data = users[username]
    user = User(username)
    return user if user_data['active'] else None

# Ruta de inicio de sesión
@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        identifier = request.form['identifier']  # Puede ser usuario o correo
        password = request.form['password']

        # Buscar si el identificador es un nombre de usuario o un correo
        user = None
        for username, details in users.items():
            if username == identifier or details['email'] == identifier:
                user = users[username]
                break

        # Validar si el usuario fue encontrado y la contraseña es correcta
        if user and user['password'] == password and user['active']:
            login_user(User(username))
            flash('Login successful!')
            return redirect(url_for('buscar_centro'))
        else:
            flash('Invalid credentials or inactive account.')
            return redirect(url_for('login'))

    return render_template('login.html')

# Ruta para buscar centros educativos
@app.route('/buscar_centro', methods=['GET', 'POST'])
@login_required
def buscar_centro():
    if request.method == 'POST':
        codigo_institucional = request.form['codigo_institucional']

        # Conectar a la base de datos
        db.connect()

        # Consulta para buscar el centro educativo
        query = """
            SELECT A.CodigoInstitucional
            FROM CentrosEducativos AS A
            WHERE A.CodigoInstitucional = ?
        """
        params = (codigo_institucional,)

        # Ejecutar la consulta con parámetros
        resultado = db.execute_query_with_params(query, params)

        db.disconnect()

        # Comprobar si se obtuvo algún resultado
        if resultado and len(resultado) > 0:
            # Si el centro existe, redirigir a la función mostrar_centro con el código institucional
            return redirect(url_for('mostrar_centro', id_centro=codigo_institucional))
        else:
            # Si no se encuentra el centro, mostrar un mensaje de error
            flash("Centro educativo no encontrado.", "danger")
            return redirect(url_for('buscar_centro'))

    # Si es GET, renderizar el formulario
    return render_template('buscar_centro.html')

# Ruta para mostrar el centro educativo y sus contactos
@app.route('/mostrar_centro/<int:id_centro>', methods=['GET'])
@login_required
def mostrar_centro(id_centro):
    # Conectar a la base de datos para obtener los detalles del centro educativo
    db.connect()
    try:
        # Obtener información del centro educativo
        query = """
            SELECT A.Nombre, B.Nombre, C.Nombre
            FROM CentrosEducativos AS A
            INNER JOIN Municipios AS B ON (A.MunicipioID = B.MunicipioID)
            INNER JOIN Departamentos AS C ON (B.DepartamentoID = C.DepartamentoID)
            WHERE A.CodigoInstitucional = ?
        """
        params = (id_centro,)
        resultado = db.execute_query_with_params(query, params)

        # Verificar si el centro existe
        if resultado and len(resultado) > 0:
            centro_info = {
                'id': id_centro,
                'nombre_centro': resultado[0][0],
                'municipio_centro': resultado[0][1],
                'departamento_centro': resultado[0][2],
            }
        else:
            # Si no se encuentra el centro, mostrar un mensaje de error
            db.disconnect()
            return "Centro educativo no encontrado", 404

        # Obtener los contactos asociados al centro usando el procedimiento almacenado
        query_contactos = "EXEC ObtenerContactosPorCodigoInstitucional ?"
        params_contactos = (id_centro,)
        resultado_contactos = db.execute_query_with_params(query_contactos, params_contactos)

        # Procesar los datos de contactos
        contactos = {}
        if resultado_contactos:
            for row in resultado_contactos:
                nombre = row[0]
                cargo = row[1]
                numero = row[2]
                tipo = row[3] if len(row) > 3 else None  # Asegurarse de que 'tipo' exista

                if nombre not in contactos:
                    contactos[nombre] = {
                        'Nombre': nombre,
                        'Cargo': cargo,
                        'Telefonos': []
                    }
                if numero:
                    contactos[nombre]['Telefonos'].append({
                        'Numero': numero,
                        'Tipo': tipo
                    })
            # Convertir el diccionario a una lista
            contactos_list = list(contactos.values())
        else:
            contactos_list = []

    except Exception as e:
        db.disconnect()
        return f"Error al obtener los datos: {e}", 500
    finally:
        db.disconnect()

    # Renderizar la página con la información del centro y los contactos
    return render_template('mostrar_centro.html', centro=centro_info, contactos=contactos_list)

# Ruta para agregar contactos al centro
@app.route('/agregar_contacto/<int:id_centro>', methods=['POST'])
@login_required
def agregar_contacto(id_centro):
    nombre_contacto = request.form['nombre_contacto']

    try:
        db.connect()  # Conectar a la base de datos

        # Ejecutar el procedimiento almacenado para insertar la persona
        query = """
                EXEC [dbo].[InsertarPersona] @CodigoInstitucional = ?, @Nombre = ?;
            """
        params = (id_centro, nombre_contacto)
        db.execute_query_with_params(query, params)

        # Obtener el PersonaID de la persona recién insertada o existente
        queryPersona = """
            SELECT PersonaID FROM [dbo].[Personas] WHERE Nombre = ?
        """
        params = (nombre_contacto,)
        result = db.execute_query_with_params(queryPersona, params, True)

        if result and result[0] is not None:
            persona_id = result[0][0]
            print(f"PersonaID insertado/encontrado: {persona_id}")

            # Obtener los teléfonos y sus tipos
            telefonos = request.form.getlist('telefonos[]')  # Lista de números de teléfono
            tipos_telefono = request.form.getlist('tipo_telefono[]')  # Lista de tipos de teléfono

            # Lista de valores permitidos para 'Tipo' (ajústalo según lo que la base de datos permita)
            tipos_permitidos = ['CELULAR', 'DOMICILIO', 'TRABAJO']  # Cambiar según valores válidos en la base de datos

            # Insertar los teléfonos relacionados con la persona
            for telefono, tipo in zip(telefonos, tipos_telefono):
                tipo = tipo.upper()  # Asegurarse de que el tipo esté en mayúsculas
                if tipo in tipos_permitidos:
                    # Insertar el teléfono si el tipo es válido
                    db.execute_query_with_params("""
                        INSERT INTO Telefonos (Numero, Tipo, PersonaID) 
                        VALUES (?, ?, ?)
                    """, (telefono, tipo, persona_id), True)
                else:
                    # Si el tipo es inválido, mostrar un error y evitar el INSERT
                    flash(f'Tipo de teléfono inválido: {tipo}', 'danger')
                    return redirect(url_for('mostrar_centro', id_centro=id_centro))

            # Confirmar la transacción si todo está bien
            db.connection.commit()
            flash('Contacto y teléfonos agregados exitosamente.', 'success')
        else:
            flash('No se pudo insertar el contacto o ya existe.', 'danger')

    except Exception as e:
        # Hacer rollback si hay un error
        db.connection.rollback()
        db.log_error('Agregar Contacto', str(e))
        flash(f'Error al agregar contacto: {e}', 'danger')

    finally:
        # Asegurarse de desconectar la base de datos
        db.disconnect()

    return redirect(url_for('mostrar_centro', id_centro=id_centro))


# Ruta de dashboard (si es necesario)
@app.route('/dashboard')
@login_required
def dashboard():
    return f"Hello, {current_user.id}! Welcome to your dashboard."

# Ruta de cierre de sesión
@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.')
    return redirect(url_for('login'))


if __name__ == '__main__':
    app.run(debug=True)
