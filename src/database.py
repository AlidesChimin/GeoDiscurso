import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from src.models import Base

class DatabaseManager:
    _instance = None
    
    def __init__(self):
        self.engine = None
        self.session_factory = None
        self.Session = None
        self.db_path = None

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def initialize_db(self, db_path):
        """
        Inicializa a conexão com o banco SQLite em db_path e cria as tabelas se não existirem.
        """
        self.db_path = db_path
        # Conecta ao SQLite com suporte a foreign keys
        self.engine = create_engine(
            f"sqlite:///{db_path}",
            connect_args={"check_same_thread": False}
        )
        
        # Habilitar foreign keys no SQLite
        from sqlalchemy import event
        @event.listens_for(self.engine, "connect")
        def set_sqlite_pragma(dbapi_connection, connection_record):
            cursor = dbapi_connection.cursor()
            cursor.execute("PRAGMA foreign_keys=ON")
            cursor.close()
            
        Base.metadata.create_all(self.engine)
        
        self.session_factory = sessionmaker(bind=self.engine)
        self.Session = scoped_session(self.session_factory)

    def get_session(self):
        if self.Session is None:
            raise Exception("Banco de dados não inicializado. Abra ou crie um projeto primeiro.")
        return self.Session()

    def close(self):
        if self.Session:
            self.Session.remove()
            self.Session = None
        if self.engine:
            self.engine.dispose()
            self.engine = None
        self.db_path = None
