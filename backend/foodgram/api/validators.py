from rest_framework import serializers


def validate_username(username):
    if username == 'me':
        raise serializers.ValidationError("Использовать имя 'me' запрещено")
    return username
