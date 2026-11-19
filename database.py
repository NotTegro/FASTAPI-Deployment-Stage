# Connects FastAPI to SQLAlchemy

# from sqlalchemy import create_engine  # Creates connection interface to SQLAlchemy for communication
# from sqlalchemy.orm import DeclarativeBase, sessionmaker    # Foundation of defining database tables | Creates sessions to query and change data

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

from config import settings

# Chooses which database to use
# SQLALCHEMY_DATABASE_URL = "sqlite+aiosqlite:///./blog.db"  # sqlite (Database type) | /// (filesystem path for SQLite) | ./blog.db (Database file) 



# Create Main interface for communication
engine = create_async_engine(
    settings.database_url,    # Selects database file
    # connect_args={"check_same_thread": False},  # Allows database connection to thread that created it. SQLite only
)

# Creating database sessions - object used for interaction (view, edit, etc)
# SessionLocal = sessionmaker(
#     autocommit=False,   # Turns off auto permanent commits each change
#     autoflush=False,    # Turns off auto temporary commits each change
#     bind=engine         # Connects sessions to main interface database
# )

AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,  # Prevents issues with expired objects
)


# Inherits and uses simplified name to be called in models.py
class Base(DeclarativeBase):    # Foundation of defining database tables
    pass


# Function to connect to database
async def get_db():
    async with AsyncSessionLocal() as session:  # Creates new database session as db, ensures closed after block finished using "with"
        yield session                # Stores session object
        