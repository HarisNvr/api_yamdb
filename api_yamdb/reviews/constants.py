MX_CHARS = 50
MX_CHARS_BIG = 256
MX_CHARS_STR = 20
MIN_REVIEW_SCORE = 1
MAX_REVIEW_SCORE = 10
ALLOWED_METHODS = [
    'get',
    'post',
    'head',
    'options',
    'delete',
    'patch',
    'trace'
]
ROLE_USER = 'user'
ROLE_MODERATOR = 'moderator'
ROLE_ADMIN = 'admin'
ROLE_CHOISE = (
    (ROLE_USER, 'Пользователь'),
    (ROLE_MODERATOR, 'Модератор'),
    (ROLE_ADMIN, 'Администратор')
)
CONFIRMATION_CODE_LEN = 6
EMAIL_LEN = 254
USERNAME_LEN = 150
