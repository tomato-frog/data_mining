from sqlalchemy import Integer, Column, String


class WithId:
    id = Column(Integer, primary_key=True, autoincrement=True)


class WithUrl:
    url = Column(String, unique=True, nullable=False)
