from sqlalchemy import Column, Integer, String
from database import Base, engine, session


class Event(Base):
    __tablename__ = "events"

    id = Column(Integer, primary_key=True)
    name = Column(String(250))
    salary = Column(Integer)
    description = Column(String(1000))
    creator_id = Column(Integer)
    message_id = Column(Integer)


    @classmethod
    def get(cls, event_id: str) -> "Event":
        event = session.query(cls).filter(cls.id == event_id).one()
        return event


Base.metadata.create_all(engine)

