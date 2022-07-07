import os


class Config:
    DEBUG = False
    DEVELOPMENT = False
    SECRET_KEY = os.getenv("SECRET_KEY", "this-is-the-default-key")
    MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
    DB_NAME = os.getenv("DB_NAME", "Development")


class ProductionConfig(Config):
    pass


class DevelopmentConfig(Config):
    DEBUG = True
    DEVELOPMENT = True
