from sqlmodel import Session, SQLModel, create_engine

class Postgres:
    init: bool = False
    
    def __init__(self, url: str):
        self.engine = create_engine(url)
        self.init = True
        self.__create_db_and_tables()

    def __create_db_and_tables(self):
        SQLModel.metadata.create_all(self.engine)

    def get_session(self):
        with Session(self.engine) as session:   
            yield session