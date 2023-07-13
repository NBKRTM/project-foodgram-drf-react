from django.core.validators import RegexValidator


def create_hex_validator():
    return RegexValidator(
        regex=r'^#[a-fA-F0-9]{6}$',
        message='Недопустимый цветовой HEX-код.'
    )


def create_slug_validator():
    return RegexValidator(
        regex=r'^[-a-zA-Z0-9_]+$',
        message='Недопустимый символ в графе slug.'
    )
