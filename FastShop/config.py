# Configuración de la base de datos MySQL
class Config:
    # Configuración de SQLAlchemy
    SQLALCHEMY_DATABASE_URI = 'mysql+mysqlconnector://root:fastshop#2026.@localhost:3306/fastshop_db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Clave secreta para sesiones (Flask-Login)
    SECRET_KEY = 'fastshop-secret-key-2026'
    
DEBUG = True