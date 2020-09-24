
class Config:
    """Basic configuration class"""
    DB_HOST = 'localhost' # Ip address of PostgreSQL server
    DB_PORT = '5432' # Port of PostgreSQL server
    DB_DATABASE = 'generaldb' # Database name
    DB_USER = 'bogus' # Database username
    DB_PASSWORD = '1'   # User password
    SECRET_KEY = '7f6af09b5132d5a0898f28034b6accd1f' #Secret key of app, used as hash salt
