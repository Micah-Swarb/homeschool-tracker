import os
import sys
import pytest

# Provide a stub for flask_migrate if it's not installed
import types
flask_migrate = types.ModuleType("flask_migrate")
flask_migrate.Migrate = lambda *args, **kwargs: None
sys.modules.setdefault("flask_migrate", flask_migrate)

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from src.main import app as flask_app
from src.models import db


@pytest.fixture
def app():
    flask_app.config.update(
        {
            "TESTING": True,
            "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
            "SECRET_KEY": "test_secret_key_for_testing_purposes_1234567890",
            "WTF_CSRF_ENABLED": False,
        }
    )
    with flask_app.app_context():
        db.create_all()
        yield flask_app
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    return app.test_client()
