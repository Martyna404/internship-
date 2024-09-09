from sqlalchemy.orm import Session
from . import models, schemas

# Player 

def get_player(db: Session, player_id: int):
    return db.query(models.Player).filter(models.Player.id == player_id).first()

def create_player(db: Session, player: schemas.PlayerCreate):
    db_player = models.Player(**player.dict())
    db.add(db_player)
    db.commit()
    db.refresh(db_player)
    return db_player

def update_player(db: Session, player_id: int, player: schemas.PlayerCreate):
    db_player = db.query(models.Player).filter(models.Player.id == player_id).first()
    if not db_player:
        return None
    for key, value in player.dict().items():
        setattr(db_player, key, value)
    db.commit()
    db.refresh(db_player)
    return db_player

def delete_player(db: Session, player_id: int):
    db_player = db.query(models.Player).filter(models.Player.id == player_id).first()
    if db_player:
        db.delete(db_player)
        db.commit()
    return db_player

# Round 

def get_round(db: Session, round_id: int):
    return db.query(models.Round).filter(models.Round.id == round_id).first()

def create_round(db: Session, round: schemas.RoundCreate):
    db_round = models.Round(**round.dict())
    db.add(db_round)
    db.commit()
    db.refresh(db_round)
    return db_round

def update_round(db: Session, round_id: int, round: schemas.RoundCreate):
    db_round = db.query(models.Round).filter(models.Round.id == round_id).first()
    if not db_round:
        return None
    for key, value in round.dict().items():
        setattr(db_round, key, value)
    db.commit()
    db.refresh(db_round)
    return db_round

def delete_round(db: Session, round_id: int):
    db_round = db.query(models.Round).filter(models.Round.id == round_id).first()
    if db_round:
        db.delete(db_round)
        db.commit()
    return db_round

# Match 

def get_match(db: Session, match_id: int):
    return db.query(models.Match).filter(models.Match.id == match_id).first()

def create_match(db: Session, match: schemas.MatchCreate):
    db_match = models.Match(**match.dict())
    db.add(db_match)
    db.commit()
    db.refresh(db_match)
    return db_match

def update_match(db: Session, match_id: int, match: schemas.MatchCreate):
    db_match = db.query(models.Match).filter(models.Match.id == match_id).first()
    if not db_match:
        return None
    for key, value in match.dict().items():
        setattr(db_match, key, value)
    db.commit()
    db.refresh(db_match)
    return db_match

def delete_match(db: Session, match_id: int):
    db_match = db.query(models.Match).filter(models.Match.id == match_id).first()
    if db_match:
        db.delete(db_match)
        db.commit()
    return db_match

# Results 

def get_result(db: Session, match_id: int):
    return db.query(models.Results).filter(models.Results.match_id == match_id).first()

def create_result(db: Session, result: schemas.ResultCreate):
    db_result = models.Results(**result.dict())
    db.add(db_result)
    db.commit()
    db.refresh(db_result)
    return db_result

def update_result(db: Session, match_id: int, result: schemas.ResultCreate):
    db_result = db.query(models.Results).filter(models.Results.match_id == match_id).first()
    if not db_result:
        return None
    for key, value in result.dict().items():
        setattr(db_result, key, value)
    db.commit()
    db.refresh(db_result)
    return db_result

def delete_result(db: Session, match_id: int):
    db_result = db.query(models.Results).filter(models.Results.match_id == match_id).first()
    if db_result:
        db.delete(db_result)
        db.commit()
    return db_result
