from tests.helper import create_user


LOGIN_URL = '/api/v2/auth/login'


def test_login_by_username(db, client):
    session = db()
    password = '123456'
    user = create_user(password)
    session.save(user)

    res = client.post(
        LOGIN_URL,
        data={
            'username': user.userName,
            'password': password,
            'isInstalled': 0,
        },
    )
    assert res.status_code == 200
    assert res.json['accessToken'] is not None
    assert res.json['refreshToken'] is not None
    assert res.json['user']['id'] is not None

    # when password is wrong
    res = client.post(
        LOGIN_URL,
        data={
            'username': user.userName,
            'password': 'wrong-password',
            'isInstalled': 0,
        },
    )
    assert res.status_code == 400

    # TODO: and more...
