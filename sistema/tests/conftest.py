import pytest

from sistema import create_app
from sistema.db import init_db


@pytest.fixture
def app(tmp_path):
    app = create_app({"TESTING": True, "DATABASE": str(tmp_path / "test.db"),
                      "SECRET_KEY": "test"})
    with app.app_context():
        init_db()
    return app


@pytest.fixture
def client(app):
    return app.test_client()


class AuthActions:
    def __init__(self, client):
        self._client = client

    def login(self, username="tecnico", password="tecnico123"):
        return self._client.post("/login", data={"username": username, "password": password})

    def login_admin(self):
        return self.login("admin", "admin123")

    def login_tecnico(self):
        return self.login("tecnico", "tecnico123")


@pytest.fixture
def auth(client):
    return AuthActions(client)
