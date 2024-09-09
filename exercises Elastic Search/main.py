import json
from mpservices.elastic_dsl import ElasticSearch_DSL
from model_elastic import SportEvent, Sevent, Stage, Season, Tournament, Discipline
from pydantic import ValidationError

class ElasticProcessor:
    def __init__(self, id: str):
        self.id = id
        self.client = ElasticSearch_DSL().Client
        self.document_data = {}

    def search_main_event(self):
        response = self.client.search(
            index="s_event_api",
            query={"match": {"record.sevent.fields.baseId": self.id}}
        )
        if response.get('hits', {}).get('hits'):
            self.document_data['sevent'] = response['hits']['hits'][0]['_source']['record']['sevent']['fields']
        else:
            raise RuntimeError(f"No data found: {self.id}")

    def search_stage(self, base_id):
        response = self.client.search(
            index="s_stage_api",
            query={"match": {"_id": f"sstage_{base_id}"}}
        )
        if response.get('hits', {}).get('hits'):
            self.document_data['sstage'] = response['hits']['hits'][0]['_source']['record']['sstage']['fields']

    def search_season(self, base_id):
        response = self.client.search(
            index="s_season_api",
            query={"match": {"_id": f"sseason_{base_id}"}}
        )
        if response.get('hits', {}).get('hits'):
            self.document_data['sseason'] = response['hits']['hits'][0]['_source']['record']['sseason']['fields']

    def search_tournament(self, base_id):
        response = self.client.search(
            index="s_tournament_api",
            query={"match": {"_id": f"stournament_{base_id}"}}
        )
        if response.get('hits', {}).get('hits'):
            self.document_data['stournament'] = response['hits']['hits'][0]['_source']['record']['stournament']['fields']

    def search_discipline(self, base_id):
        response = self.client.search(
            index="s_discipline_api",
            query={"match": {"_id": f"sdiscipline_{base_id}"}}
        )
        if response.get('hits', {}).get('hits'):
            self.document_data['sdiscipline'] = response['hits']['hits'][0]['_source']['record']['sdiscipline']['fields']

    def process_event(self):
        self.search_main_event()

        if self.document_data.get('sevent', {}).get('baseStageId'):
            self.search_stage(self.document_data['sevent']['baseStageId'])

        if self.document_data.get('sstage', {}).get('baseSeasonId'):
            self.search_season(self.document_data['sstage']['baseSeasonId'])

        if self.document_data.get('sseason', {}).get('baseTournamentId'):
            self.search_tournament(self.document_data['sseason']['baseTournamentId'])

        if self.document_data.get('sstage', {}).get('baseDisciplineId'):
            self.search_discipline(self.document_data['sstage']['baseDisciplineId'])

    def fill_missing_values(self, data: dict, required_fields: dict):
        for field, field_info in required_fields.items():
            if field not in data:
                if field_info.annotation == int:
                    data[field] = 0  
                elif field_info.annotation == str:
                    data[field] = "notfound"  
        return data

    def get_final_model(self) -> SportEvent:
        sevent_data = self.fill_missing_values(self.document_data.get('sevent', {}), Sevent.model_fields)
        stage_data = self.fill_missing_values(self.document_data.get('sstage', {}), Stage.model_fields)
        season_data = self.fill_missing_values(self.document_data.get('sseason', {}), Season.model_fields)
        tournament_data = self.fill_missing_values(self.document_data.get('stournament', {}), Tournament.model_fields)
        discipline_data = self.fill_missing_values(self.document_data.get('sdiscipline', {}), Discipline.model_fields)

        sport_event = SportEvent(
            sevent=Sevent(**sevent_data),
            stage=Stage(**stage_data),
            season=Season(**season_data),
            tournament=Tournament(**tournament_data),
            discipline=Discipline(**discipline_data)
        )
        return sport_event

    @staticmethod
    def get_random_ids(size=10):
        client = ElasticSearch_DSL().Client
        response = client.search(
            index="s_event_api",
            size=size,
            query={
                "function_score": {
                    "query": {
                        "match_all": {}
                    },
                    "random_score": {}
                }
            }
        )
        if not response.get('hits', {}).get('hits'):
            raise RuntimeError("problem with generating random ids")

        random_base_ids = [hit['_source']['record']['sevent']['fields']['baseId'] for hit in response['hits']['hits']]
        return random_base_ids


random_ids = ElasticProcessor.get_random_ids()

for base_id in random_ids:
    elastic_instance = ElasticProcessor(id=base_id)
    elastic_instance.process_event()
    final_model = elastic_instance.get_final_model()
    try:
        validated = SportEvent.model_validate(final_model.dict()) 
        json_output = validated.model_dump_json(by_alias=True, indent=4)  
        print(json_output)
    except ValidationError as e:
        print('problem with validation', e)


print()
