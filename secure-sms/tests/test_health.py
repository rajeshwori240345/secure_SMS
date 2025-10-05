"""Basic health tests for the Secure SMS application.

These tests ensure that core routes behave as expected.  They are
 intentionally minimal to encourage adding more comprehensive tests in
 future iterations.
"""

from run import app



def test_root_redirects_to_login() -> None:
    """Ensure the root path redirects unauthenticated users to /login."""
    client = app.test_client()
    resp = client.get('/', follow_redirects=False)
    # Expect redirect (301 or 302) to /login
    assert resp.status_code in (301, 302)
    loc = resp.headers.get('Location', '')
    assert '/login' in loc