from ..models import User

# /////////////////////////////////////////////////////////////////////////
# Register tests


def test_register_user_success(client):
    """
    Test successful user registration
    """
    user_data = {
        "first_name": "Zaki",
        "last_name": "Ayoubi",
        "email": "zaki@markviz.com",
        "password": "zaki1212",
    }

    response = client.post("/auth/register", json=user_data)

    assert response.status_code == 201
    assert response.json()["message"] == "User registered successfully"
    assert response.json()["email"] == "zaki@markviz.com"


def test_register_user_duplicate_email(client):
    """
    Test that registering with duplicate email fails
    """
    user_data = {
        "first_name": "Zaki",
        "last_name": "Ayoubi",
        "email": "zaki@markviz.com",
        "password": "zaki1212",
    }

    # Register first time
    response1 = client.post("/auth/register", json=user_data)
    assert response1.status_code == 201

    # Register a second time with the same email and it should fail
    response2 = client.post("/auth/register", json=user_data)
    assert response2.status_code == 400
    assert response2.json()["detail"] == "Email already registered"


def test_register_user_missing_fields(client):
    """
    Test that registration with missing required fields fail
    """
    user_data = {
        "last_name": "Ayoubi",
        "email": "zaki@markviz.com",
        "password": "zaki1212",
    }

    response = client.post("/auth/register", json=user_data)
    assert response.status_code == 422  # Validation error


def test_register_user_invalid_email(client):
    """
    Test that registration fails with bad email
    """
    user_data = {
        "first_name": "Zaki",
        "last_name": "Ayoubi",
        "email": "zaki.markviz.com",
        "password": "zaki1212",
    }

    response = client.post("/auth/register", json=user_data)
    assert response.status_code == 422  # Validation error


def test_register_user_password_is_hashed(client, db):
    """
    Test that is not stored in plain text
    """
    user_data = {
        "first_name": "Zaki",
        "last_name": "Ayoubi",
        "email": "zaki@markviz.com",
        "password": "zaki1212",
    }

    response = client.post("/auth/register", json=user_data)
    assert response.status_code == 201

    # Check database directly
    user = db.query(User).filter(User.email == "zaki@markviz.com").first()
    assert user is not None
    assert user.hashed_password != user_data["password"]


# /////////////////////////////////////////////////////////////////////////
# Login tests


def test_login_success(client, registered_user):
    """
    Test that user can successfully login
    """

    login_data = {"email": "zaki@markviz.com", "password": "zaki1212"}

    login_response = client.post("/auth/login", json=login_data)
    assert login_response.status_code == 200
    assert "token" in login_response.json()
    assert login_response.json()["token_type"] == "bearer"


def test_login_incorrect_password(client, registered_user):
    """
    Test that login should fail with incorrect password
    """
    login_data = {"email": "zaki@markviz.com", "password": "incorrect_pass"}

    response = client.post("auth/login", json=login_data)
    assert response.status_code == 401
    assert response.json()["detail"] == "Incorrect email or password"


def test_login_non_existent_user(client, registered_user):
    """
    Test that a login attempt with a non-existent email should fail
    """
    login_data = {"email": "mark@markviz.com", "password": "some_pass"}

    response = client.post("/auth/login", json=login_data)
    assert response.status_code == 401
    assert response.json()["detail"] == "Incorrect email or password"


def test_login_missing_fields(client, registered_user):
    response = client.post("/auth/login", json={"email": "zaki@markviz.com"})

    assert response.status_code == 422


def test_login_invalid_email_format(client, registered_user):
    login_data = {
        "email": "not-an-email",
        "password": "zaki1212",
    }

    response = client.post("/auth/login", json=login_data)

    assert response.status_code == 422
