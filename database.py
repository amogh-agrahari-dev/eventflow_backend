import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

# Create engine with connection pooling enabled for serverless Postgres
engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,  # Ensures dead connections are recycled
    pool_size=5,
    max_overflow=10,
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


# Dependency to yield DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()