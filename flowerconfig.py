import os

def get_secret(secret_name, default=None):
    try:
        with open(f'/run/secrets/{secret_name}', 'r') as secret_file:
            return secret_file.read().strip()
    except IOError:
        env_name = secret_name.upper().replace('-', '_')
        return os.environ.get(env_name, default)


USERNAME = 'dev'
PASSWORD = get_secret('flower-password', 'changeit')

basic_auth = [f'{USERNAME}:{PASSWORD}']
