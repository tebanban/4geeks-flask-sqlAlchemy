import os
from flask import Flask, request, jsonify, url_for, abort
from flask_migrate import Migrate
from flask_swagger import swagger
from flask_cors import CORS
from utils import APIException, generate_sitemap
from admin import setup_admin
from models import db, User

app = Flask(__name__)
app.url_map.strict_slashes = False
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DB_CONNECTION_STRING')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
MIGRATE = Migrate(app, db)
db.init_app(app)
CORS(app)
setup_admin(app)

# Handle/serialize errors like a JSON object
@app.errorhandler(APIException)
def handle_invalid_usage(error):
    return jsonify(error.to_dict()), error.status_code

# generate sitemap with all your endpoints
@app.route('/')
def sitemap():
    return generate_sitemap(app)

@app.route('/user', methods=['GET'])
def get_all_users():
    all_users = User.query.all()
    serialized_users = [user.serialize() for user in all_users]
    return jsonify(serialized_users)

@app.route('/user', methods=['POST'])
def post_user():
    try:
        user_data = request.json
        new_user = User()
        new_user.email = user_data['email']
        new_user.password = user_data['password']
        new_user.is_active = True
    except:
        raise APIException('POST request must contain json containing keys and values for email and password.')
    
    try:
        db.session.add(new_user)
        db.session.commit()
    except:
        raise APIException('Email already exists')

    serialized_users = [user.serialize() for user in User.query.all()]
    return jsonify(serialized_users)
    

@app.route('/user/<int:id>', methods=['GET'])
def get_user(id):
    user = User.query.get(id)
    if user == None:
        raise APIException(f'Unable to locate user id: {id}')
    return jsonify(user.serialize())

@app.route('/user/<int:id>', methods=['DELETE'])
def delete_user(id):
    user = User.query.get(id)
    if user == None:
        raise APIException(f'Unable to locate user id: {id}')
    db.session.delete(user)
    db.session.commit()
    serialized_users = [user.serialize() for user in User.query.all()]
    return jsonify(serialized_users)

@app.route('/user/<int:id>', methods=['PUT'])
def update_user(id):
    user = User.query.get(id)
    if user == None:
        raise APIException(f'Unable to locate user id: {id}')
    user_data = request.json
    user.email = user_data['email']
    user.password = user_data['password']
    user.is_active = True
    try:
        db.session.commit()
    except:
        raise APIException(f'The email {user_data["email"]} already exists')
    return jsonify(user.serialize())

if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=False)
