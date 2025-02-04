from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField
from wtforms.validators import DataRequired, Length, EqualTo

class SignUpForm(FlaskForm):
    username = StringField('아이디', validators=[
        DataRequired(message='아이디를 입력해주세요'),
        Length(min=4, max=20, message='아이디는 4-20자 사이여야 합니다')
    ])
    password = PasswordField('비밀번호', validators=[
        DataRequired(message='비밀번호를 입력해주세요'),
        Length(min=6, message='비밀번호는 최소 6자 이상이어야 합니다')
    ])
    confirm_password = PasswordField('비밀번호 확인', validators=[
        DataRequired(message='비밀번호 확인을 입력해주세요'),
        EqualTo('password', message='비밀번호가 일치하지 않습니다')
    ])
