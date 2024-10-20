from flask_sqlalchemy import SQLAlchemy

#Initialize SQLAlchemy 
db = SQLAlchemy()

#Import the models (this allows other parts of the app to access the models)
from .budget import Budget
from .investment import Investment