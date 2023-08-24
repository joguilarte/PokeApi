from flask import Flask, jsonify, request
from flask_jwt_extended import (
    JWTManager, jwt_required, create_access_token,
    get_jwt_identity
)
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import requests
import random
import configparser
import logging

app = Flask(__name__)

# Configurar el registro de Flask
logging.basicConfig(level=logging.INFO)

# Leer el archivo de configuración
config = configparser.ConfigParser()
config.read('config.cfg')

# Configuración de Flask-JWT-Extended
app.config['JWT_SECRET_KEY'] = config['DEFAULT']['JWT_SECRET_KEY']
jwt = JWTManager(app)

# Configuración de Flask-SQLAlchemy
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)

    def __init__(self, username, password, is_admin=False):
        self.username = username
        self.password = generate_password_hash(password)
        self.is_admin = is_admin

    def check_password(self, password):
        return check_password_hash(self.password, password)

with app.app_context():
    db.create_all()
  

BASE_URL = "https://pokeapi.co/api/v2/"

# Endpoint para crear un nuevo token de acceso
@app.route('/login', methods=['POST'])
def login():
    username = request.json.get('username', None)
    password = request.json.get('password', None)
    
    try:
        user = User.query.filter_by(username=username).first()
    except Exception as e:
        app.logger.error(f'Error al consultar la base de datos: {e}')
        return jsonify({"msg": "Lo siento, hubo un problema al consultar la base de datos. Por favor, inténtalo de nuevo más tarde o contacta al soporte técnico si el problema persiste."}), 500
    
    if not user or not user.check_password(password):
        app.logger.warning(f'Intento fallido de inicio de sesión para el usuario {username}')
        return jsonify({"msg": "Credenciales incorrectas"}), 401

    access_token = create_access_token(identity=username)
    app.logger.info(f'Usuario {username} inició sesión con éxito')
    return jsonify(access_token=access_token)

# Endpoint para registrar un nuevo usuario
@app.route('/register', methods=['POST'])
@jwt_required()
def register():
    current_user = get_jwt_identity()
    user = User.query.filter_by(username=current_user).first()
    if not user.is_admin:
        app.logger.warning(f'Usuario {current_user} intentó registrar un nuevo usuario sin permisos de administrador')
        return jsonify({"msg": "No tienes permisos para realizar esta acción"}), 403

    username = request.json.get('username', None)
    password = request.json.get('password', None)
    if not username or not password:
        app.logger.warning(f'Faltan datos para registrar un nuevo usuario')
        return jsonify({"msg": "Faltan datos"}), 400
    
    try:
        user = User(username, password)
        db.session.add(user)
        db.session.commit()
    except Exception as e:
        app.logger.error(f'Error al guardar el nuevo usuario en la base de datos: {e}')
        return jsonify({"msg": "Lo siento, hubo un problema al guardar el nuevo usuario en la base de datos. Por favor, verifica que los datos ingresados sean correctos e inténtalo de nuevo más tarde o contacta al soporte técnico si el problema persiste."}), 500
    
    app.logger.info(f'Usuario {username} registrado con éxito por el administrador {current_user}')
    
    return jsonify({"msg": "Usuario registrado con éxito"})


# Endpoint para listar usuarios 
@app.route('/list_users', methods=['GET'])
@jwt_required()
def list_users():
    current_user = get_jwt_identity()
    user = User.query.filter_by(username=current_user).first()
    if not user.is_admin:
        app.logger.warning(f'Usuario {current_user} intentó listar usuarios sin permisos de administrador')
        return jsonify({"msg": "No tienes permisos para realizar esta acción"}), 403

    users = User.query.all()
    users_list = [{"username": u.username, "is_admin": u.is_admin} for u in users]
    
    app.logger.info(f'Usuario {current_user} listó usuarios con éxito')
    
    return jsonify(users_list)

# Endpoint para eliminar un usuarios
@app.route('/delete_user', methods=['DELETE'])
@jwt_required()
def delete_user():
    current_user = get_jwt_identity()
    user = User.query.filter_by(username=current_user).first()
    if not user.is_admin:
        app.logger.warning(f'Usuario {current_user} intentó eliminar un usuario sin permisos de administrador')
        return jsonify({"msg": "No tienes permisos para realizar esta acción"}), 403

    username = request.json.get('username', None)
    if not username:
        app.logger.warning(f'Faltan datos para eliminar un usuario')
        return jsonify({"msg": "Faltan datos"}), 400

    user = User.query.filter_by(username=username).first()
    if not user:
        app.logger.warning(f'El usuario {username} no existe')
        return jsonify({"msg": "El usuario no existe"}), 404

    db.session.delete(user)
    db.session.commit()
    
    app.logger.info(f'Usuario {username} eliminado con éxito por el administrador {current_user}')
    
    return jsonify({"msg": "Usuario eliminado con éxito"})

# Endpoint para obtener los tipos de un Pokémon segun su nombre
@app.route("/pokemon/type/<name>")
@jwt_required()
def get_pokemon_type(name):
    # Verificar que el parámetro name solo contenga letras
    if not name.isalpha():
        return jsonify({"msg": "El nombre del Pokémon solo debe contener letras"}), 400
    
    try:
        response = requests.get(f"{BASE_URL}pokemon/{name}")
    except Exception as e:
        app.logger.error(f'Error al hacer la solicitud a la API externa: {e}')
        return jsonify({"msg": "Lo siento, hubo un problema al hacer la solicitud a la API externa. Por favor, verifica tu conexión a Internet e inténtalo de nuevo más tarde o contacta al soporte técnico si el problema persiste."}), 500
    
    data = response.json()
    types = [t["type"]["name"] for t in data["types"]]
    
    app.logger.info(f'Tipos de Pokémon {name} obtenidos con éxito')
    
    return jsonify(types)

# Endpoint para obtener un Pokémon aleatorio de un tipo específico
@app.route("/pokemon/random/<type>")
@jwt_required()
def get_random_pokemon(type):
    # Verificar que el parámetro type solo contenga letras
    if not type.isalpha():
        return jsonify({"msg": "El tipo de Pokémon solo debe contener letras"}), 400
    
    try:
        response = requests.get(f"{BASE_URL}type/{type}")
    except Exception as e:
        app.logger.error(f'Error al hacer la solicitud a la API externa: {e}')
        return jsonify({"msg": "Lo siento, hubo un problema al hacer la solicitud a la API externa. Por favor, verifica tu conexión a Internet e inténtalo de nuevo más tarde o contacta al soporte técnico si el problema persiste."}), 500
    
    data = response.json()
    pokemon = data["pokemon"]
    random_pokemon = random.choice(pokemon)["pokemon"]["name"]
    
    app.logger.info(f'Pokémon aleatorio de tipo {type} obtenido con éxito: {random_pokemon}')
    
    return jsonify(random_pokemon)

# Endpoint para obtener el Pokémon con el nombre más largo de un tipo específico
@app.route("/pokemon/longest-name/<type>")
@jwt_required()
def get_longest_name_pokemon(type):
    # Verificar que el parámetro type solo contenga letras
    if not type.isalpha():
        return jsonify({"msg": "El tipo de Pokémon solo debe contener letras"}), 400
    
    try:
        response = requests.get(f"{BASE_URL}type/{type}")
    except Exception as e:
        app.logger.error(f'Error al hacer la solicitud a la API externa: {e}')
        return jsonify({"msg": "Lo siento, hubo un problema al hacer la solicitud a la API externa. Por favor, verifica tu conexión a Internet e inténtalo de nuevo más tarde o contacta al soporte técnico si el problema persiste."}), 500
    
    data = response.json()
    pokemon = data["pokemon"]
    longest_name_pokemon = max(pokemon, key=lambda p: len(p["pokemon"]["name"].split("-")[0]))["pokemon"]["name"].split("-")[0]
    
    app.logger.info(f'Pokémon con el nombre más largo de tipo {type} obtenido con éxito: {longest_name_pokemon}')
    
    return jsonify(longest_name_pokemon)



if __name__ == "__main__":
    app.run(host='0.0.0.0')
