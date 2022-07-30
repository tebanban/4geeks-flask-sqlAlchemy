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
    user_data = request.json
    new_user = User()
    new_user.email = user_data['email']
    new_user.password = user_data['password']
    new_user.is_active = True
    db.session.add(new_user)
    db.session.commit()
    serialized_users = [user.serialize() for user in User.query.all()]
    return jsonify(serialized_users)

@app.route('/user/<int:id>', methods=['GET'])
def get_user(id):
    try: 
        user = User.query.get(id)
        return jsonify(user.serialize())
    except:
        raise APIException(f'Unable to locate user: {id}')

if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=False)
