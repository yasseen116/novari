from flask import Flask,render_template
from flask_sqlalchemy import SQLAlchemy
from flask_restful import Api
import mysql.connector
from flask_login import LoginManager
import os 
from flask_cors import CORS
from flask_migrate import Migrate





# Initialize extensions
db = SQLAlchemy()
api = Api()
basedir = os.path.abspath(os.path.dirname(__file__))

def create_db():
    db.create_all()
    print("database created")

def create_app():
    app = Flask(__name__)

    # Configuration inside __init__.py
    app.config['SECRET_KEY'] = "topsecret"
    app.config['SQLALCHEMY_DATABASE_URI'] = "mysql+mysqlconnector://root:asd%40123@localhost/novari_06"
    app.config['UPLOAD_FOLDER'] = os.path.join(basedir, 'static/uploads')

    from app.routes.api import api_bp

    # Initialize extensions with the app
    db.init_app(app)
    api.init_app(app)
    CORS(app)  # Allow all origins (or configure as needed)
    migrate = Migrate(app, db)

    @app.errorhandler(404)
    def page_not_found(error):
        return render_template('404.html')


    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'

    @login_manager.user_loader
    def load_user(id):
        return Customer.query.get(int(id))

    @login_manager.unauthorized_handler
    def unauthorized():
        from flask import jsonify, request, redirect, url_for
        if request.is_json or request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({'success': False, 'message': 'Login required'}), 401
        return redirect(url_for('auth.login'))

    from app import models
    from app import forms


    from app.routes.views import views  # Import the views blueprint
    from app.routes.auth import auth  # Import the views blueprint
    from app.routes.admin import admin  # Import the views blueprint
    from app.models import Customer,Cart,Category,Product,Wishlist


    app.register_blueprint(views, url_prefix='/')
    app.register_blueprint(admin, url_prefix='/admin')
    app.register_blueprint(auth, url_prefix='/auth')
    app.register_blueprint(api_bp, url_prefix='/api')

    # Database initialization (creates tables if not exist)
    with app.app_context():
       create_db()

    # Inject 'now' into all templates
    from datetime import datetime
    @app.context_processor
    def inject_now():
        return {'now': datetime.now()}

    return app