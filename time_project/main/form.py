from flask_wtf import FlaskForm
from wtforms import ValidationError,StringField,PasswordField,SubmitField,TimeField,IntegerField,RadioField
from wtforms.validators import DataRequired,Optional
from time_project.models import User

class Loginform(FlaskForm):
    users_id = StringField('ID', validators=[DataRequired()])
    password = PasswordField('パスワード',validators=[DataRequired()])
    submit = SubmitField('ログイン')
    
class Registrationform(FlaskForm):
     username = StringField('従業員名',validators=[DataRequired()])
     users_id = StringField('従業員ID',validators=[DataRequired()])
     employment_type = RadioField('雇用形態', choices=[('parttime','アルバイト'),('fulltime','正社員')], default='parttime')
     hourly_wage = IntegerField('時給(アルバイト用)', validators=[Optional()])
     fixed_wage = IntegerField('固定給(正社員用)', validators=[Optional()])
     password = PasswordField('パスワード',validators=[DataRequired()])
     pass_confirm = PasswordField('パスワード（確認）',validators=[DataRequired()])
     submit = SubmitField('登録')

     def validate_username(self, field):
          if User.query.filter_by(username = field.data).first():
               raise ValidationError('入力した名前は既に使われています。')
          
     def validate_users_id(self,field):
          if User.query.filter_by(users_id = field.data).first():
               raise ValidationError('入力したIDは既に使われています。')
          
     def validate(self, extra_validators=None):
          if not super().validate(extra_validators=extra_validators):
               return False

          if not self.hourly_wage.data and not self.fixed_wage.data:
               self.hourly_wage.errors.append('時給か固定給のどちらかを入力してください。')
               return False

          if self.employment_type.data == 'fulltime' and not self.fixed_wage.data:
               self.fixed_wage.errors.append('正社員には固定給の入力が必要です。')
               return False

          if self.employment_type.data == 'parttime' and not self.hourly_wage.data:
               self.hourly_wage.errors.append('アルバイトには時給の入力が必要です。')
               return False

          return True
     

class UpdateUserform(FlaskForm):
     username = StringField('従業員名',validators=[DataRequired()])
     users_id = StringField('従業員ID',validators=[DataRequired()])
     employment_type = RadioField('雇用形態', choices=[('parttime','アルバイト'),('fulltime','正社員')],
                                  default='parttime',render_kw={"class": "form-check-input"})
     hourly_wage = StringField('時給', validators=[Optional()])
     fixed_wage = StringField('固定給', validators=[Optional()])
     password = PasswordField('パスワード',validators=[DataRequired()])
     pass_confirm = PasswordField('パスワード（確認）',validators=[DataRequired()])
     submit = SubmitField('変更')

     def __init__(self,user_id,*args,**kwargs):
          super(UpdateUserform,self).__init__(*args,**kwargs)
          self.id = user_id
          
     def validate_username(self,field):
          if User.query.filter(User.id != self.id ).filter_by(username = field.data).first():
               raise ValidationError('入力した名前は既に使われています。')
          
     def validate_users_id(self,field):
          if User.query.filter(User.id != self.id ).filter_by(users_id = field.data).first():
               raise ValidationError('入力したIDは既に使われています。')
     def validate(self, extra_validators=None):
          if not super().validate(extra_validators=extra_validators):
               return False

          if not self.hourly_wage.data and not self.fixed_wage.data:
               self.hourly_wage.errors.append('時給か固定給のどちらかを入力してください。')
               return False

          if self.employment_type.data == 'fulltime' and not self.fixed_wage.data:
               self.fixed_wage.errors.append('正社員には固定給の入力が必要です。')
               return False

          if self.employment_type.data == 'parttime' and not self.hourly_wage.data:
               self.hourly_wage.errors.append('アルバイトには時給の入力が必要です。')
               return False

          return True
          

class TimeCorrectform(FlaskForm):
     check_in = TimeField('出勤時刻',validators=[Optional()])
     check_out = TimeField('退勤時刻', validators=[Optional()])
     rest_in = TimeField('休憩時刻',validators=[Optional()])
     rest_out = TimeField('復帰時刻', validators=[Optional()])
     submit = SubmitField('変更')
          

