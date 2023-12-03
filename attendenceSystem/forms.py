from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed, FileRequired
from flask_login import current_user
from wtforms import StringField, PasswordField, SubmitField, BooleanField,IntegerField, RadioField
from wtforms.validators import DataRequired, Length, Email, EqualTo,ValidationError
from attendenceSystem.models import User
# from flask_uploads import UploadSet, IMAGES

# images = UploadSet('images', IMAGES)

class RegistrationForm(FlaskForm):
    rollno = IntegerField('Id/RollNo',validators=[DataRequired()]) #rollnumber
    name=StringField('Name',validators=[DataRequired(), Length(min=1, max=50)])
    upload = FileField('Image', validators=[FileRequired(),FileAllowed(['jpg','png','jpeg'], 'Images only!')])
    section = RadioField('Section', choices=[('Coordinator', 'Coordinator'),('2A', '2A'), ('2B', '2B'),('2C', '2C'), ('2D', '2D'),('2E', '2E'), ('2F', '2F')],validators=[DataRequired()])
    email = StringField('Email',validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=8, max=12)])
    confirm_password = PasswordField('Confirm Password',validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Sign Up')

    # def validate_username(self, username):
    #     user = User.query.filter_by(username=username.data).first()
    #     if user:
    #         raise ValidationError('That username is taken. Please choose a different one.')
        
    def validate_rollno(self, rollno):
        user = User.query.filter_by(rollno=rollno.data).first()
        if user:
            raise ValidationError('That rollno is taken. Please choose a different one.')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('That email is taken. Please choose a different one.')


class LoginForm(FlaskForm):
    # email = StringField('Email',validators=[DataRequired(), Email()])
    id = IntegerField('Id',validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Login')



class UpdateAccountForm(FlaskForm):
    rollno = IntegerField('Id/RollNo',validators=[DataRequired()]) #rollnumber
    name=StringField('Name',validators=[DataRequired(), Length(min=1, max=50)])
    upload = FileField('Update Profile Picture', validators=[FileAllowed(['jpg','png','jpeg'], 'Images only!')])
    section = RadioField('Section', choices=[('Coordinator', 'Coordinator'),('2A', '2A'), ('2B', '2B'),('2C', '2C'), ('2D', '2D'),('2E', '2E'), ('2F', '2F')])
    email = StringField('Email',validators=[DataRequired(), Email()])
    submit = SubmitField('Update')
    # password = PasswordField('Password', validators=[Length(min=0, max=12)])
    # confirm_password = PasswordField('Confirm Password',validators=[EqualTo('password')])

    def validate_username(self, rollno):
        if rollno.data != current_user.rollno:
            user = User.query.filter_by(username=rollno.data).first()
            if user:
                raise ValidationError('That rollno is taken. Please choose a different one.')

    def validate_email(self, email):
        if email.data != current_user.email:
            user = User.query.filter_by(email=email.data).first()
            if user:
                raise ValidationError('That email is taken. Please choose a different one.')
            