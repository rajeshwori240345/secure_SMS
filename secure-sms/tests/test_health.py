import re
from run import app

def test_root_redirects_to_login():
    client = app.test_client()
    resp = client.get('/', follow_redirects=False)
    # Expect redirect (302) to /login
    assert resp.status_code in (301, 302)
    loc = resp.headers.get('Location','')
    assert '/login' in loc
