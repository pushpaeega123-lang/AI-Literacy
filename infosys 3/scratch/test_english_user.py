import requests

s = requests.Session()
login_res = s.post('http://127.0.0.1:5500/login_user', data={
    'email': 'john@example.com',
    'password': 'Password123!'
}, allow_redirects=True)

print('Login request final URL:', login_res.url)
print('Login request status:', login_res.status_code)

home_res = s.get('http://127.0.0.1:5500/')
print('Home page contains "Logout":', 'Logout' in home_res.text)
print('Home page contains "Dashboard":', 'Dashboard' in home_res.text)
