from sqlmodel import SQLModel, Session, create_engine
from models import settings
# connect_args is needed for SQLite (NOT PostgreSQL) to work properly with multi-threaded FastAPI
engine = create_engine(settings.DATABASE_URL)

def get_session():
    with Session(engine) as session:
        yield session
           
        
def create_db_and_tables():
    """Create database tables based on SQLModel schemas."""
    SQLModel.metadata.create_all(engine)