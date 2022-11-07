from db_seeder.seeder import seed
from app.database import models
from app.database.database import SessionLocal


seed(models, SessionLocal)
