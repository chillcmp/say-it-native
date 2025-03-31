from app.db.session import Base, engine


def init_db():
    from app.models import user, text_edit, usage_log, api_key
    Base.metadata.create_all(bind=engine)

if __name__ == "__main__":
    init_db()
