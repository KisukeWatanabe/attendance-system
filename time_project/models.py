from time_project import db, login_manager
from flask_login import UserMixin
from werkzeug.security import check_password_hash,generate_password_hash
from datetime import datetime
from pytz import timezone

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)

class User(db.Model, UserMixin):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64))
    users_id = db.Column(db.String(64),unique=True, nullable=False)

    employment_type = db.Column(db.String(10), nullable=False,default='parttime')
    hourly_wage = db.Column(db.Integer,nullable=True)
    fixed_wage = db.Column(db.Integer,nullable=True)
    
    password_hash = db.Column(db.String(256))
    administrator = db.Column(db.String(1))
    Timepage_records = db.relationship('Timepage',backref ='user',lazy='dynamic',cascade='all, delete-orphan')

    def __init__(self,username,users_id, password,administrator,employment_type=None,hourly_wage=None,fixed_wage=None):
        self.username = username
        self.users_id = users_id
        self.password = password
        self.administrator = administrator
        self.employment_type = employment_type
        self.hourly_wage = hourly_wage
        self.fixed_wage = fixed_wage
         

    def __repr__(self):
        return f"UserName: {self.username}"
    
    def checkpassword(self,password):
        return check_password_hash(self.password_hash,password)
    
    @property
    def password(self):
        raise ArithmeticError('password is not a readable attribute')
    @property
    def employment_display(self):
        if self.employment_type == "fulltime":
            return "正社員"
        elif self.employment_type == "parttime":
            return "アルバイト・パート"
        else:
            return "未設定"

    @property
    def wage_display(self):
        if self.employment_type == "fulltime":
            # 固定給（負になっても0表示）S
            wage = self.fixed_wage if self.fixed_wage and self.fixed_wage > 0 else 0
            return f"{wage:,}円"
        elif self.employment_type == "parttime":
            # 時給（負を0円表示）
            wage = self.hourly_wage if self.hourly_wage and self.hourly_wage > 0 else 0
            return f"{wage:,}円"
        else:
            return "未設定"
        
    @password.setter
    def password(self,password):
        self.password_hash = generate_password_hash(password)
    @property
    def is_administrator(self):
        return self.administrator == "1"
        
class Timepage(db.Model):
    __tablename__ = 'timepages'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    date = db.Column(db.Date,nullable=False)
    check_in= db.Column(db.Time,nullable=True)
    check_out = db.Column(db.Time,nullable=True)
    rest_in = db.Column(db.Time,nullable=True)
    rest_out = db.Column(db.Time,nullable=True)
    correct = db.Column(db.Boolean, default=False)
    status = db.Column(db.String(20), default="none")

    
    def __init__(self,user_id,date):
        self.user_id = user_id
        self.date = date



    
    

    




    