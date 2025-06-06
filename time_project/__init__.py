import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from dotenv import load_dotenv


app = Flask(__name__)

#絶対パスの参照
load_dotenv()
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
basedir = os.path.abspath(os.path.dirname(__file__))
uri = os.getenv('DATABASE_URL')

if uri and uri.startswith("postgres://"):
    uri = uri.replace("postgres://", "postgresql://", 1)

app.config['SQLALCHEMY_DATABASE_URI'] = uri
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
Migrate(app,db)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'main.login'

##*args,**kwargsは文字とか格納したいときに使う
def localize_callback (*args,**kwargs):
    return 'このページにアクセスするには、ログインが必要です。'
login_manager.localize_callback = localize_callback

# ユーザーのロード関数（必須）
@login_manager.user_loader
def load_user(user_id):
    from time_project.models import User  # models.py から User クラスをインポート
    return User.query.get(int(user_id))


from time_project.main.views import main
from time_project.error_pages.handlers import error_pages

app.register_blueprint(main)
app.register_blueprint(error_pages)

