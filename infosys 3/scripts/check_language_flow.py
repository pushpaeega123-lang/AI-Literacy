import requests

session = requests.Session()

# select Telugu
response = session.post('http://127.0.0.1:5500/language', data={'language': 'Telugu'})
print('language select status:', response.status_code, 'redirected to', response.url)
register = session.get('http://127.0.0.1:5500/register')
print('register length:', len(register.text))
print('TELUGU REGISTER LABEL FOUND:', 'పూర్తి పేరు' in register.text)
print('TELUGU LANGUAGE OPTION FOUND:', 'తెలుగు' in register.text)
print('LOGIN PAGE TELUGU LABEL FOUND:', 'ఇమెయిల్ చిరునామా' in session.get('http://127.0.0.1:5500/login').text)
