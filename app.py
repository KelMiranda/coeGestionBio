from flask import Flask, render_template, redirect, url_for, request, flash
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from datetime import timedelta
from dotenv import load_dotenv
from database.sql_server_connection import SQLServerDatabase

app = Flask(__name__)
app.secret_key = ',btqS$NE@+dr}^L&?<C6'  # Cambia esto por una clave secreta segura
app.permanent_session_lifetime = timedelta(minutes=10)  # Tiempo máximo de inactividad antes de cerrar la sesión

# Cargar las variables de entorno
load_dotenv()
db = SQLServerDatabase('SQL_SERVER', 'SQL_DATABASE', 'SQL_USERNAME', 'SQL_PASSWORD')

# Configuración de Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Simulación de usuarios (normalmente obtendrías los usuarios de una base de datos)
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


@app.route('/buscar_centro', methods=['GET', 'POST'])
@login_required
def buscar_centro():
    if request.method == 'POST':
        codigo_institucional = request.form['codigo_institucional']

        # Conectar a la base de datos
        db.connect()

        # Consulta para buscar el centro educativo
        query = """
            SELECT A.Nombre, B.Nombre, C.Nombre
            FROM CentrosEducativos AS A
            INNER JOIN Municipios AS B ON (A.MunicipioID = B.MunicipioID)
            INNER JOIN Departamentos AS C ON (B.DepartamentoID = C.DepartamentoID)
            WHERE A.CodigoInstitucional = ?
        """
        params = (codigo_institucional,)

        # Ejecutar la consulta con parámetros
        resultado = db.execute_query_with_params(query, params)

        db.disconnect()

        # Comprobar si se obtuvo algún resultado
        if resultado and len(resultado) > 0:
            # Construir el diccionario con la información del centro
            centro_info = {
                'id': codigo_institucional,
                'nombre_centro': resultado[0][0],
                'municipio_centro': resultado[0][1],
                'departamento_centro': resultado[0][2],
            }

            # Renderizar el template con la información del centro
            return render_template('mostrar_centro.html', centro=centro_info)
        else:
            # Si no se encuentra el centro, mostrar un mensaje de error
            return "Centro educativo no encontrado", 404

    # Si es GET, renderizar el formulario
    return render_template('buscar_centro.html')


@app.route('/mostrar_centro/<int:id_centro>', methods=['GET'])
@login_required
def mostrar_centro(id_centro):
    # Conectar a la base de datos para obtener los detalles del centro educativo
    db.connect()

    query = """
        SELECT A.Nombre, B.Nombre, C.Nombre
        FROM CentrosEducativos AS A
        INNER JOIN Municipios AS B ON (A.MunicipioID = B.MunicipioID)
        INNER JOIN Departamentos AS C ON (B.DepartamentoID = C.DepartamentoID)
        WHERE A.CodigoInstitucional = ?
    """
    params = (id_centro,)
    resultado = db.execute_query_with_params(query, params)

    db.disconnect()

    # Verificar si el centro existe
    if resultado and len(resultado) > 0:
        centro_info = {
            'id': id_centro,
            'nombre_centro': resultado[0][0],
            'municipio_centro': resultado[0][1],
            'departamento_centro': resultado[0][2],
        }
        # Renderizar la página con la información del centro
        return render_template('mostrar_centro.html', centro=centro_info)
    else:
        # Si no se encuentra el centro, mostrar un mensaje de error
        return "Centro educativo no encontrado", 404

@app.route('/agregar_contacto/<int:id_centro>', methods=['POST'])
@login_required
def agregar_contacto(id_centro):
    # Obtener los datos del formulario
    nombre_contacto = request.form['nombre_contacto']
    telefonos = request.form.getlist('telefonos[]')  # Lista de números de teléfono
    tipos_telefono = request.form.getlist('tipo_telefono[]')  # Lista de tipos de teléfono
    print(nombre_contacto, telefonos, tipos_telefono)
    # Procesar los datos y guardarlos en la base de datos
    # Aquí podrías insertar el contacto y los teléfonos en tu base de datos

    # Por ejemplo, insertar el contacto y luego los teléfonos relacionados a ese contacto.
    # Código de ejemplo para insertar en la base de datos:
    # db.execute("INSERT INTO contactos (nombre, centro_id) VALUES (?, ?)", (nombre_contacto, id_centro))
    # for telefono, tipo in zip(telefonos, tipos_telefono):
    #     db.execute("INSERT INTO telefonos (numero, tipo, contacto_id) VALUES (?, ?, ?)", (telefono, tipo, contacto_id))

    # Redireccionar de vuelta a la página del centro educativo
    return redirect(url_for('mostrar_centro', id_centro=id_centro))


@app.route('/dashboard')
@login_required
def dashboard():
    return f"Hello, {current_user.id}! Welcome to your dashboard."


@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.')
    return redirect(url_for('login'))


if __name__ == '__main__':
    app.run(debug=True)
