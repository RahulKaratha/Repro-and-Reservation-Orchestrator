class Config:
    SECRET_KEY = "your_secret_key"
    SQLALCHEMY_DATABASE_URI = "mysql+mysqlconnector://root:yourpassword@localhost/reproreservationdb"
    SQLALCHEMY_TRACK_MODIFICATIONS = False