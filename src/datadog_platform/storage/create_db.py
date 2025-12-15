
from datadog_platform.storage.models import Base, get_engine

def create_db_tables():
    engine = get_engine()
    Base.metadata.create_all(engine)
    print("Database tables created successfully.")

if __name__ == "__main__":
    create_db_tables()
