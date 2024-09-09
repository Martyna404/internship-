from pydantic import BaseModel
from typing import List, Optional



class Episode(BaseModel):
    num : int
    title : str
    title_lang : Optional[str] = None
    date : Optional[str] = None
    director : Optional[str] = None

class Season(BaseModel):
    num_season: Optional[int] = None
    episodes : List[Episode]


class Person(BaseModel):
    name:str
    url: Optional[str]


class WikipediaResult(BaseModel):
    Languages: dict[str, 'WikipediaSerie']



class WikipediaSerie(BaseModel):
    title_org :Optional[str] = None
    title :Optional[str] = None
    premiere_date : Optional[str] = None
    cast : Optional[List[Person]] = None
    directors : Optional[List[Person]] = None
    seasons : Optional[List[Season]] = None
