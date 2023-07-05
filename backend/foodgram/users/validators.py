from django.core.validators import RegexValidator


def create_username_validator():
    return RegexValidator(
        regex=r'^[\w.@+-]+$',
        message='Недопустимое имя пользователя.'
    )
