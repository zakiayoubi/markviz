from app.database import engine, Base
from app.models import User, Holding

print("Creating tables...")

Base.metadata.create_all(bind=engine)

print("Tables created successfully!")
print("- users")
print("- holdings")
