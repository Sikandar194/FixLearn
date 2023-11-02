import os
import redis


class Config:
    SECRET_KEY = 'your-secret-key'
    SQLALCHEMY_DATABASE_URI = "mssql+pyodbc:///?odbc_connect=DRIVER%3D%7BSQL+Server+Native+Client+11.0%7D%3BServer%3DDESKTOP-RGGQBCN%5CSQLEXPRESS%3BDatabase%3DCourse%3BTrusted_Connection%3Dyes%3BPort%3D1433"
    #SQLALCHEMY_DATABASE_URI = "mssql+pyodbc://shaheertest_SQLLogin_1:2wfcyl22k8@Courses.mssql.somee.com/Courses?driver=SQL+Server+Native+Client+11.0"
    #SQLALCHEMY_DATABASE_URI = "mssql+pyodbc://shaheertest_SQLLogin_1:2wfcyl22k8@Courses.mssql.somee.com/Courses"

    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_PORT = '465'
    MAIL_USE_SSL = True
    MAIL_USERNAME = 'bizintro1@gmail.com'
    MAIL_PASSWORD = "mcgjjvnhbfbrabgo"
    CELERY_BROKER_URL = 'redis://localhost:6379/0'
    CELERY_RESULT_BACKEND = 'redis://localhost:6379/0'
    SESSION_TYPE = 'redis'
    SECRET_KEY = 'your-secret-key'
    CELERY_BROKER_URL = 'redis://localhost:6379/0'
    CELERY_RESULT_BACKEND = 'redis://localhost:6379/0'
    SESSION_PERMANENT = True
    SESSION_COOKIE_SECURE = True  # Requires HTTPS
    SESSION_COOKIE_HTTPONLY = True
    SESSION_USE_SIGNER = True
    SESSION_KEY_PREFIX = 'your_prefix:'
    SESSION_REDIS = redis.StrictRedis(
        host= 'localhost',
        port= 6379,
        db = 0
    )
