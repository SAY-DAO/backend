from say.helpers import get_secret


USERNAME = 'dev'
PASSWORD = get_secret('flower-password', 'dev')

basic_auth = [f'{USERNAME}:{PASSWORD}']
