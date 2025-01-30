from .views import app
from . import models

# Connect sqlalchemy to app
models.db.init_app(app)
