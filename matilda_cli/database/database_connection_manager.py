import colorama  # Ajout de colorama
from sqlalchemy import MetaData, create_engine

colorama.init(autoreset=True)


class DatabaseConnectionManager:
    """
    Manages the database connection, engine, and metadata reflection.
    """

    def __init__(self, db_url: str):
        self.db_url = db_url
        self.engine = create_engine(db_url)
        self.metadata = MetaData()
        self.metadata.reflect(bind=self.engine)
        self.conn = self.engine.connect()

    def close(self):
        if self.conn:
            self.conn.close()
            self.engine.dispose()
            self.conn = None
            self.engine = None
