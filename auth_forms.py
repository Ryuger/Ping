from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SelectField, BooleanField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, Length, ValidationError, EqualTo
from models import User, UserRole

class LoginForm(FlaskForm):
    """Форма входа в систему"""
    username = StringField('Имя пользователя', validators=[
        DataRequired(message='Введите имя пользователя'),
        Length(min=3, max=80, message='Имя пользователя должно быть от 3 до 80 символов')
    ])
    password = PasswordField('Пароль', validators=[
        DataRequired(message='Введите пароль')
    ])
    remember_me = BooleanField('Запомнить меня')
    submit = SubmitField('Войти')

class CreateUserForm(FlaskForm):
    """Форма создания пользователя"""
    username = StringField('Имя пользователя', validators=[
        DataRequired(message='Введите имя пользователя'),
        Length(min=3, max=80, message='Имя пользователя должно быть от 3 до 80 символов')
    ])
    password = PasswordField('Пароль', validators=[
        DataRequired(message='Введите пароль'),
        Length(min=6, message='Пароль должен быть не менее 6 символов')
    ])
    password_confirm = PasswordField('Подтверждение пароля', validators=[
        DataRequired(message='Подтвердите пароль'),
        EqualTo('password', message='Пароли не совпадают')
    ])
    role = SelectField('Роль', choices=[
        (UserRole.VIEWER.value, 'Только просмотр'),
        (UserRole.USER.value, 'Пользователь'),
        (UserRole.ADMIN.value, 'Администратор'),
        (UserRole.SUPERADMIN.value, 'Суперадмин')
    ], validators=[DataRequired()])
    submit = SubmitField('Создать пользователя')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('Пользователь с таким именем уже существует')

class EditUserForm(FlaskForm):
    """Форма редактирования пользователя"""
    username = StringField('Имя пользователя', validators=[
        DataRequired(message='Введите имя пользователя'),
        Length(min=3, max=80, message='Имя пользователя должно быть от 3 до 80 символов')
    ])
    role = SelectField('Роль', choices=[
        (UserRole.VIEWER.value, 'Только просмотр'),
        (UserRole.USER.value, 'Пользователь'),
        (UserRole.ADMIN.value, 'Администратор'),
        (UserRole.SUPERADMIN.value, 'Суперадмин')
    ], validators=[DataRequired()])
    is_active = BooleanField('Активен')
    submit = SubmitField('Сохранить изменения')

class ChangePasswordForm(FlaskForm):
    """Форма смены пароля"""
    current_password = PasswordField('Текущий пароль', validators=[
        DataRequired(message='Введите текущий пароль')
    ])
    new_password = PasswordField('Новый пароль', validators=[
        DataRequired(message='Введите новый пароль'),
        Length(min=8, message='Пароль должен быть не менее 8 символов')
    ])
    new_password_confirm = PasswordField('Подтверждение нового пароля', validators=[
        DataRequired(message='Подтвердите новый пароль'),
        EqualTo('new_password', message='Пароли не совпадают')
    ])
    submit = SubmitField('Сменить пароль')

class ForcePasswordChangeForm(FlaskForm):
    """Форма принудительной смены пароля"""
    current_password = PasswordField('Текущий пароль', validators=[
        DataRequired(message='Введите текущий пароль')
    ])
    new_password = PasswordField('Новый пароль', validators=[
        DataRequired(message='Введите новый пароль'),
        Length(min=8, message='Пароль должен быть не менее 8 символов')
    ])
    confirm_password = PasswordField('Подтверждение нового пароля', validators=[
        DataRequired(message='Подтвердите новый пароль'),
        EqualTo('new_password', message='Пароли не совпадают')
    ])
    submit = SubmitField('Изменить пароль')

class ResetPasswordForm(FlaskForm):
    """Форма сброса пароля администратором"""
    new_password = PasswordField('Новый пароль', validators=[
        DataRequired(message='Введите новый пароль'),
        Length(min=6, message='Пароль должен быть не менее 6 символов')
    ])
    new_password_confirm = PasswordField('Подтверждение пароля', validators=[
        DataRequired(message='Подтвердите пароль'),
        EqualTo('new_password', message='Пароли не совпадают')
    ])
    submit = SubmitField('Сбросить пароль')

class UnlockUserForm(FlaskForm):
    """Форма разблокировки пользователя"""
    submit = SubmitField('Разблокировать пользователя')

class AuditLogFilterForm(FlaskForm):
    """Форма фильтрации журнала аудита"""
    username = StringField('Имя пользователя')
    action = StringField('Действие')
    submit = SubmitField('Фильтровать')