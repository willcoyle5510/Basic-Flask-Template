import uuid
from app import app, DATABASE

client = app.test_client()
email = 'test_' + uuid.uuid4().hex[:8] + '@example.com'
password = 'Password123'

register_resp = client.post(
    '/register',
    data={
        'firstname': 'Test',
        'lastname': 'User',
        'email': email,
        'password': password,
        'confirm_password': password,
    },
    follow_redirects=False,
)

login_resp = client.post(
    '/',
    data={'email': email, 'password': password},
    follow_redirects=False,
)

print('register_status', register_resp.status_code, register_resp.headers.get('Location'))
print('login_status', login_resp.status_code, login_resp.headers.get('Location'))
print('db_rows', DATABASE.ViewQuery('SELECT email, password FROM users WHERE email = ?', (email,)))
