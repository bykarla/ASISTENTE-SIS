from app.core.database import engine
from app.models.orm import Base

if __name__ == "__main__":
    Base.metadata.create_all(bind=engine)
    print("Tablas creadas")