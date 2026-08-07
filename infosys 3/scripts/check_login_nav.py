import requests

s = requests.Session()
login = s.post('http://127.0.0.1:5500/login_user', data={'email':'ram@example.com','password':'TeluguPass1!'}, allow_redirects=True)
print('Login status:', login.status_code)
home = s.get('http://127.0.0.1:5500/')
if 'Logout' in home.text:
    print('Logout link present in navbar')
else:
    print('Logout link NOT present')

assessment = s.get('http://127.0.0.1:5500/assessment')
print('Assessment page status:', assessment.status_code)
if 'పనిచేసే నిపుణుడు' in assessment.text:
    print('VERIFICATION SUCCESS: Telugu label for professional age group found!')
else:
    print('VERIFICATION FAILURE: Expected label not found in assessment response')

