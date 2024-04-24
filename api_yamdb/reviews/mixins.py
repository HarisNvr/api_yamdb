import re

from django.core.exceptions import ValidationError


class UsernameValidatorMixin:
    def validate_username(self, username):
        print('start')
        if username == 'me':
            raise ValidationError('Имя пользователя "me" недопустимо.')
        forbidden_chars = re.sub(r'[a-zA-Z0-9_]', '', username)
        if forbidden_chars:
            raise ValidationError(f'{username}содержит недопустимые'
                                  f'символы: {forbidden_chars}')
        print('end')
        return username
