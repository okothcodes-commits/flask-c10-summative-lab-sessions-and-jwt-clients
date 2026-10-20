import os


class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "development-only-secret-key")
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL", "sqlite:///app.db")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    CORS_ORIGINS = os.environ.get("CORS_ORIGINS", "http://localhost:3000").split(",")
    JSON_SORT_KEYS = False


class DevelopmentConfig(Config):
    DEBUG = os.environ.get("FLASK_DEBUG", "0") == "1"


class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"


class ProductionConfig(Config):
    DEBUG = False
