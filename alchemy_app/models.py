from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, Date
from sqlalchemy.orm import relationship
from .database import Base

class Player(Base):
    __tablename__ = "player"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, index=True,nullable=False)
    surname = Column(String,nullable=False)

    matches = relationship("Match", back_populates="player")
    results_won = relationship("Results", foreign_keys='Results.player_won', back_populates="player_won_ref")
    results_lost = relationship("Results", foreign_keys='Results.player_loss', back_populates="player_loss_ref")


class Round(Base):
    __tablename__ = "round"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, index=True)
    date = Column(Date)
    no = Column(Integer)

    matches = relationship("Match", back_populates="round")

class Match(Base):
    __tablename__ = "match"

    id = Column(Integer, primary_key=True, autoincrement=True)
    round_id = Column(Integer, ForeignKey('round.id'))
    player_id = Column(Integer, ForeignKey('player.id'))
    order_no = Column(Integer)

    round = relationship("Round", back_populates="matches")
    player = relationship("Player", back_populates="matches")
    result = relationship("Results", uselist=False, back_populates="match")

class Results(Base):
    __tablename__ = "results"

    match_id = Column(Integer, ForeignKey('match.id'), primary_key=True)
    player_won = Column(Integer, ForeignKey('player.id'))
    player_loss = Column(Integer, ForeignKey('player.id'))
    result = Column(String)

    match = relationship("Match", back_populates="result")
    player_won_ref = relationship("Player", foreign_keys=[player_won], back_populates="results_won")
    player_loss_ref = relationship("Player", foreign_keys=[player_loss], back_populates="results_lost")
