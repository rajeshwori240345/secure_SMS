from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, SelectField
from wtforms.validators import DataRequired, Email, Length, EqualTo

class LoginForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField("Login")

class RegisterForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired(), Length(min=3, max=80)])
    email = StringField("Email", validators=[DataRequired(), Email(), Length(max=120)])
    password = PasswordField("Password", validators=[DataRequired(), Length(min=8)])
    confirm = PasswordField("Confirm Password", validators=[DataRequired(), EqualTo("password")])
    role = SelectField("Role", choices=[("student","Student"),("teacher","Teacher"),("admin","Admin")])
    submit = SubmitField("Register")

class OTPForm(FlaskForm):
    code = StringField("One-Time Password", validators=[DataRequired(), Length(min=6, max=6)])
    submit = SubmitField("Verify OTP")

class StudentForm(FlaskForm):
    name = StringField("Name", validators=[DataRequired(), Length(min=2, max=120)])
    email = StringField("Email", validators=[DataRequired(), Email(), Length(max=120)])
    address = StringField("Address")
    grade = SelectField("Grade", choices=[("A","A"),("B","B"),("C","C"),("D","D"),("F","F")])
    submit = SubmitField("Save")

class TeacherForm(FlaskForm):
    name = StringField("Name", validators=[DataRequired(), Length(min=2, max=120)])
    email = StringField("Email", validators=[DataRequired(), Email(), Length(max=120)])
    department = StringField("Department")
    submit = SubmitField("Save")
