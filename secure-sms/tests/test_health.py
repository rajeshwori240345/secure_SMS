import json
from app.app import app

def test_health_endpoint():
    client = app.test_client()
    resp = client.get('/health')
    assert resp.status_code == 200
    payload = resp.get_json()
    assert payload.get('status') == 'ok'
