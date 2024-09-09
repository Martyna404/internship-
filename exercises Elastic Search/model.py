from pydantic import BaseModel, ConfigDict
from typing import Optional
from pydantic.alias_generators import to_camel
 
class Schema(BaseModel):
    model_config = ConfigDict(
        alias_generator = to_camel,
        populate_by_name=True,
        from_attributes=True,
    )
 
class Sevent(Schema):
    base_id : int
    base_name_lang_df: Optional[str] = "notfound"
    base_stage_id: int
    base_season_id: int
    base_tournament_id: int
 
class Stage(Schema):
    base_id : int
    base_fullname_lang_df: Optional[str] = "notfound"
    base_discipline_id: int
 
 
class Season(Schema):
    base_id : int
    base_fullname_lang_df: Optional[str] = "notfound"
 
 
class Tournament(Schema):
    base_id : int
    base_fullname_lang_df: Optional[str] = "notfound"
 
class Discipline(Schema):
    base_id : int
    base_fullname_lang_df: Optional[str] = "notfound"
 
 
class SportEvent(BaseModel):
    sevent : Sevent
    stage : Stage
    season : Season
    tournament : Tournament
    discipline : Discipline
