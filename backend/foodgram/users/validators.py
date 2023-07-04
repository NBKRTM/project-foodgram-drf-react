from django.core.validators import RegexValidator


def create_username_validator():
    return RegexValidator(
        regex=r'^[\w.@+-]+\z',
        message='Недопустимое имя пользователя.'
    )