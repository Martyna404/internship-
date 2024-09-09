from fastapi import FastAPI, HTTPException, Depends, Request
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime
from sql_app import models, schemas, crud
from sql_app.database import SessionLocal, engine
from sqlalchemy.orm.attributes import flag_modified
from sqlalchemy import inspect
from .kafka_producent import test, send

producer = test()

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Player

@app.post("/players/", response_model=schemas.Player)
def create_player(player: schemas.PlayerCreate, db: Session = Depends(get_db)):
    new_player = crud.create_player(db=db, player=player)

    mes = {
        "id": new_player.id,
        "name": new_player.name,
        "surname": new_player.surname
    }

    endpoint_name = 'players_post'

    send(producer, mes, key=new_player.id, headers=[("endpoint", endpoint_name.encode('utf-8'))])

    return new_player

@app.get("/players/{player_id}", response_model=schemas.Player)
def read_player(player_id: int, db: Session = Depends(get_db)):
    db_player = crud.get_player(db, player_id=player_id)
    if db_player is None:
        raise HTTPException(status_code=404, detail="Player not found")

    
    mes = {
        "id": db_player.id,
        "name": db_player.name,
        "surname": db_player.surname
    }

    endpoint_name = 'players_get'
    send(producer, mes, key=db_player.id, headers=[("endpoint", endpoint_name.encode('utf-8'))])

    return db_player




@app.put("/players/{player_id}", response_model=schemas.Player)
def update_player(player_id: int, player: schemas.PlayerCreate, db: Session = Depends(get_db)):
    db_player = crud.get_player(db=db, player_id=player_id)
    if db_player is None:
        raise HTTPException(status_code=404, detail="Player not found")

    changes = False  

    for attr in inspect(db_player).attrs:
        if attr.key == "id":  
            continue
        old_value = getattr(db_player, attr.key)
        new_value = getattr(player, attr.key, [])

        if old_value != new_value:
            setattr(db_player, attr.key, new_value)
            flag_modified(db_player, attr.key)  
            changes = True
    
    
    if changes==True:
        db.commit()  

        mes = {
            "id": db_player.id,  
            "name": db_player.name,
            "surname": db_player.surname
        }

        endpoint_name = 'players_put'
        send(producer, mes, key=db_player.id, headers=[("endpoint", endpoint_name.encode('utf-8'))])

        return db_player
    else:
        raise HTTPException(status_code=400, detail="old_value == new_value")


@app.delete("/players/{player_id}", response_model=schemas.Player)
def delete_player(player_id: int, db: Session = Depends(get_db)):
    db_player = crud.delete_player(db=db, player_id=player_id)
    if db_player is None:
        raise HTTPException(status_code=404, detail="Player not found")

    
    mes = {
        "id": db_player.id,
        "name": db_player.name,
        "surname": db_player.surname
    }

    endpoint_name = 'players_delete'
    send(producer, mes, key=db_player.id, headers=[("endpoint", endpoint_name.encode('utf-8'))])

    return db_player

# Round

@app.post("/rounds/", response_model=schemas.Round)
def create_round(round: schemas.RoundCreate, db: Session = Depends(get_db)):
    new_round = crud.create_round(db=db, round=round)

    mes = {
        "date": new_round.date,
        "name": new_round.name,
        "no": new_round.no,
        "id":new_round.id
    }

    endpoint_name = 'rounds_post'
    send(producer, mes, key=new_round.id, headers=[("endpoint", endpoint_name.encode('utf-8'))])

    return new_round

@app.get("/rounds/{round_id}", response_model=schemas.Round)
def read_round(round_id: int, db: Session = Depends(get_db)):
    db_round = crud.get_round(db, round_id=round_id)
    if db_round is None:
        raise HTTPException(status_code=404, detail="Round not found")

    mes = {
        "date": db_round.date,
        "name": db_round.name,
        "no": db_round.no,
        "id":db_round.id
    }

    endpoint_name = 'rounds_get'
    send(producer, mes, key=db_round.id, headers=[("endpoint", endpoint_name.encode('utf-8'))])

    return db_round

@app.put("/rounds/{round_id}", response_model=schemas.Round)
def update_round(round_id: int, round: schemas.RoundCreate, db: Session = Depends(get_db)):
    db_round = crud.update_round(db=db, round_id=round_id, round=round)
    if db_round is None:
        raise HTTPException(status_code=404, detail="Round not found")

    mes = {
        "date": db_round.date,
        "name": db_round.name,
        "no": db_round.no,
        "id":db_round.id
    }

    endpoint_name = 'rounds_put'
    send(producer, mes, key=db_round.id, headers=[("endpoint", endpoint_name.encode('utf-8'))])

    return db_round

@app.delete("/rounds/{round_id}", response_model=schemas.Round)
def delete_round(round_id: int, db: Session = Depends(get_db)):
    db_round = crud.delete_round(db=db, round_id=round_id)
    if db_round is None:
        raise HTTPException(status_code=404, detail="Round not found")

    
    mes = {
        "date": db_round.date,
        "name": db_round.name,
        "no": db_round.no,
        "id": db_round.id
    }

    endpoint_name = 'rounds_delete'
    send(producer, mes, key=db_round.id, headers=[("endpoint", endpoint_name.encode('utf-8'))])

    return db_round


# Match

@app.post("/matches/", response_model=schemas.Match)
def create_match(match: schemas.MatchCreate, db: Session = Depends(get_db)):
    new_match = crud.create_match(db=db, match=match)

    mes = {
        "round_id": new_match.round_id,
        "player_id": new_match.player_id,
        "order_no":new_match.order_no,
        "id": new_match.id
    }

    endpoint_name = 'matches_post'
    send(producer, mes, key=new_match.id, headers=[("endpoint", endpoint_name.encode('utf-8'))])

    return new_match

@app.get("/matches/{match_id}", response_model=schemas.Match)
def read_match(match_id: int, db: Session = Depends(get_db)):
    db_match = crud.get_match(db, match_id=match_id)
    if db_match is None:
        raise HTTPException(status_code=404, detail="Match not found")

    mes = {
        "round_id": db_match.round_id,
        "player_id": db_match.player_id,
        "order_no":db_match.order_no,
        "id": db_match.id
    }

    endpoint_name = 'matches_get'
    send(producer, mes, key=db_match.id, headers=[("endpoint", endpoint_name.encode('utf-8'))])

    return db_match

@app.put("/matches/{match_id}", response_model=schemas.Match)
def update_match(match_id: int, match: schemas.MatchCreate, db: Session = Depends(get_db)):
    db_match = crud.update_match(db=db, match_id=match_id, match=match)
    if db_match is None:
        raise HTTPException(status_code=404, detail="Match not found")

    mes = {
        "round_id": db_match.round_id,
        "player_id": db_match.player_id,
        "order_no":db_match.order_no,
        "id": db_match.id
    }

    endpoint_name = 'matches_put'
    send(producer, mes, key=db_match.id, headers=[("endpoint", endpoint_name.encode('utf-8'))])

    return db_match

@app.delete("/matches/{match_id}", response_model=schemas.Match)
def delete_match(match_id: int, db: Session = Depends(get_db)):
    db_match = crud.delete_match(db=db, match_id=match_id)
    if db_match is None:
        raise HTTPException(status_code=404, detail="Match not found")

    
    mes = {
        "round_id": db_match.round_id,
        "player_id": db_match.player_id,
        "order_no": db_match.order_no,
        "id": db_match.id
    }

    endpoint_name = 'matches_delete'
    send(producer, mes, key=db_match.id, headers=[("endpoint", endpoint_name.encode('utf-8'))])

    return db_match


@app.post("/results/", response_model=schemas.Result)
def create_result(result: schemas.ResultCreate, db: Session = Depends(get_db)):
    new_result = crud.create_result(db=db, result=result)

    mes = {
        "match_id": new_result.match_id,
        "player_won": new_result.player_won,
        "player_loss": new_result.player_loss,
        "result": new_result.result
    }

    endpoint_name = 'results'
    send(producer, mes, key=new_result.match_id, headers=[("endpoint", endpoint_name.encode('utf-8'))])

    return new_result

@app.get("/results/{match_id}", response_model=schemas.Result)
def read_result(match_id: int, db: Session = Depends(get_db)):
    db_result = crud.get_result(db, match_id=match_id)
    if db_result is None:
        raise HTTPException(status_code=404, detail="Result not found")

    mes = {
        "match_id": db_result.match_id,
        "player_won": db_result.player_won,
        "player_loss": db_result.player_loss,
        "result": db_result.result
    }


    endpoint_name = 'results_read'
    send(producer, mes, key=db_result.match_id, headers=[("endpoint", endpoint_name.encode('utf-8'))])

    return db_result

@app.put("/results/{match_id}", response_model=schemas.Result)
def update_result(match_id: int, result: schemas.ResultCreate, db: Session = Depends(get_db)):
    db_result = crud.update_result(db=db, match_id=match_id, result=result)
    if db_result is None:
        raise HTTPException(status_code=404, detail="Result not found")

    mes = {
        "match_id": db_result.match_id,
        "player_won": db_result.player_won,
        "player_loss": db_result.player_loss,
        "result": db_result.result
    }

    endpoint_name = 'results_update'
    send(producer, mes, key=db_result.match_id, headers=[("endpoint", endpoint_name.encode('utf-8'))])

    return db_result

@app.delete("/results/{match_id}", response_model=schemas.Result)
def delete_result(match_id: int, db: Session = Depends(get_db)):
    db_result = crud.delete_result(db=db, match_id=match_id)
    if db_result is None:
        raise HTTPException(status_code=404, detail="Result not found")

    mes = {
        "match_id": db_result.match_id,
        "player_won": db_result.player_won,
        "player_loss": db_result.player_loss,
        "result": db_result.result
    }

    endpoint_name = 'results_delete'
    send(producer, mes, key=db_result.match_id, headers=[("endpoint", endpoint_name.encode('utf-8'))])

    return db_result


#cd /workspaces/minefield/projects/mp_alchemy

#uvicorn sql_app.main:app --reload --port 8005

