import app as app_module

def test_home_page_loads():
    client = app_module.app.test_client()
    response = client.get("/")
    assert response.status_code == 200
    assert b"EFL Application" in response.data

def test_converter_page_needs_login():
    client = app_module.app.test_client()
    response = client.get("/converter")
    assert response.status_code == 302

def test_converter_page_loads_when_signed_in():
    client = app_module.app.test_client()
    with client.session_transaction() as session:
        session["user_id"] = 1
    response = client.get("/converter")
    assert response.status_code == 200
    assert b"convert-form" in response.data