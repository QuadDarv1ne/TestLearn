"""Script to create database tables."""
from app.db.database import Base, engine

# Import all models to register them
from app.db import models

print('Creating tables...')
Base.metadata.create_all(bind=engine)
print('Tables created successfully!')

import sqlite3
conn = sqlite3.connect('testlearn.db')
cursor = conn.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = [row[0] for row in cursor.fetchall()]
print('Tables:', tables)
conn.close()
