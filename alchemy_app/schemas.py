from pydantic import BaseModel
from typing import Optional
from datetime import date


class MatchBase(BaseModel):
    round_id: int
    player_id: int
    order_no: int

class MatchCreate(MatchBase):
    pass

class Match(MatchBase):
    id: int

    class Config:
        orm_mode = True

class PlayerBase(BaseModel):
    name: str
    surname: str

class PlayerCreate(PlayerBase):
    pass

class Player(PlayerBase):
    id: int

    class Config:
        orm_mode = True

class RoundBase(BaseModel):
    date: date
    name: str
    no: int

class RoundCreate(RoundBase):
    pass

class Round(RoundBase):
    id: int

    class Config:
        orm_mode = True



class ResultBase(BaseModel):
    match_id: int
    player_won: int
    player_loss: int
    result: str

class ResultCreate(ResultBase):
    pass

class Result(ResultBase):
    match_id: int  

    class Config:
        orm_mode = True


 
