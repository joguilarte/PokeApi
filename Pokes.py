from flask import Flask, jsonify, request
from flask_jwt_extended import (
    JWTManager, jwt_required, create_access_token,
    get_jwt_identity
)
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import requests
import random

app = Flask(__name__)

# Configuración de Flask-JWT-Extended
app.config['JWT_SECRET_KEY'] = 'super-secret'  # Es un secreto ;) 
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
    user = User.query.filter_by(username=username).first()
    if not user or not user.check_password(password):
        return jsonify({"msg": "Credenciales incorrectas"}), 401

    access_token = create_access_token(identity=username)
    return jsonify(access_token=access_token)

# Endpoint para registrar un nuevo usuario
@app.route('/register', methods=['POST'])
@jwt_required()
def register():
    current_user = get_jwt_identity()
    user = User.query.filter_by(username=current_user).first()
    if not user.is_admin:
        return jsonify({"msg": "No tienes permisos para realizar esta acción"}), 403

    username = request.json.get('username', None)
    password = request.json.get('password', None)
    if not username or not password:
        return jsonify({"msg": "Faltan datos"}), 400

    user = User(username, password)
    db.session.add(user)
    db.session.commit()
    return jsonify({"msg": "Usuario registrado con éxito"})


#  Listar usuarios 
@app.route('/list_users', methods=['GET'])
@jwt_required()
def list_users():
    current_user = get_jwt_identity()
    user = User.query.filter_by(username=current_user).first()
    if not user.is_admin:
        return jsonify({"msg": "No tienes permisos para realizar esta acción"}), 403

    users = User.query.all()
    users_list = [{"username": u.username, "is_admin": u.is_admin} for u in users]
    return jsonify(users_list)


# Endpoint para eliminar un usuarios
@app.route('/delete_user', methods=['DELETE'])
@jwt_required()
def delete_user():
    current_user = get_jwt_identity()
    user = User.query.filter_by(username=current_user).first()
    if not user.is_admin:
        return jsonify({"msg": "No tienes permisos para realizar esta acción"}), 403

    username = request.json.get('username', None)
    if not username:
        return jsonify({"msg": "Faltan datos"}), 400

    user = User.query.filter_by(username=username).first()
    if not user:
        return jsonify({"msg": "El usuario no existe"}), 404

    db.session.delete(user)
    db.session.commit()
    return jsonify({"msg": "Usuario eliminado con éxito"})

@app.route("/pokemon/type/<name>")
@jwt_required()
def get_pokemon_type(name):
    response = requests.get(f"{BASE_URL}pokemon/{name}")
    data = response.json()
    types = [t["type"]["name"] for t in data["types"]]
    return jsonify(types)

@app.route("/pokemon/random/<type>")
@jwt_required()
def get_random_pokemon(type):
    response = requests.get(f"{BASE_URL}type/{type}")
    data = response.json()
    pokemon = data["pokemon"]
    random_pokemon = random.choice(pokemon)["pokemon"]["name"]
    return jsonify(random_pokemon)

@app.route("/pokemon/longest-name/<type>")
@jwt_required()
def get_longest_name_pokemon(type):
    response = requests.get(f"{BASE_URL}type/{type}")
    data = response.json()
    pokemon = data["pokemon"]
    longest_name_pokemon = max(pokemon, key=lambda p: len(p["pokemon"]["name"].split("-")[0]))["pokemon"]["name"].split("-")[0]
    return jsonify(longest_name_pokemon)

if __name__ == "__main__":
    app.run()(host='0.0.0.0')
