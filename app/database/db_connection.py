import sqlalchemy
import sqlalchemy.orm
from app.config.settings import get_settings

settings = get_settings()

db_url = settings.db_connection_url
engine = sqlalchemy.create_engine(url=db_url, pool_pre_ping=True, pool_size=16)
session_local = sqlalchemy.orm.sessionmaker(bind=engine, autoflush=False)

def get_db():
    try:
        db = session_local()
        yield db
    finally:
        db.close()
