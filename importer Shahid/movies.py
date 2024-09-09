import requests
import json
from urllib.parse import urlparse, parse_qs
from typing import List
import re

HOST = "https://api2.shahid.net/proxy/v2.1"


class ShahidMovieImporter:
    def __init__(self, url: str) -> None:
        self.url = url


      # def fetch_page_content(self, id_param: int):
    #     response = requests.get(f'{HOST}/product/id?request=%7B%22id%22%3A%22{id_param}%22%2C%22productType%22%3A%22MOVIE%22%7D')
    #     if response.status_code == 200:
    #         return response.text
    #     else:
    #         raise RuntimeError(f"Failed to fetch the page: {response.status_code}")

    # def extract_language_from_url(self):
    #     parsed_url = urlparse(self.url)
    #     query_params = parse_qs(parsed_url.query)
    #     language = query_params.get('language')
    #     return language


    @staticmethod
    def extract_last_segment(url: str) -> str:
        match = re.search(r'\/([^\/]+)$', url)
        if match:
            return match.group(1)
    

    def extract_language_from_url(self):
        parsed_url = urlparse(self.url)
        query_params = parse_qs(parsed_url.query)
        language = query_params.get('language')
        return language
        
    def get_carousels(self) -> List[str]:
        response = requests.get(f'{HOST}/editorial/page?request=%7B%22pageAlias%22:%22movies%22,%22profileFolder%22:%22WW%22%7D',headers={'uuid':'WEB'})
        if response.ok:
            result = response.json()
            carousels_ids = result.get('carousels')
            carousels = []
            for carousel_id in carousels_ids:
                carousel = carousel_id.get('id')
                if carousel:
                    carousels.append(carousel)

        
        return carousels
               

    def get_item(self, id_param: int):
        response = requests.get(f'{HOST}/product/id?request=%7B%22id%22%3A%22{id_param}%22%2C%22productType%22%3A%22MOVIE%22%7D')
        if response.ok:
            result = response.json()
            root_persons = result.get("productModel", {}).get("persons", [])
            persons_list = []
            director_list = []

            for person in root_persons:
                person_data = {
                    "Id": person.get("id"),
                    "Full name": person.get("fullName")
                }
                persons_list.append(person_data)

            root_duration = result.get("productModel", {}).get("duration")
            duration_min = round(root_duration / 60,1) if root_duration else "UNKNOWN"

            if duration_min == "UNKNOWN":
                return None

            root_directors = result.get("productModel", {}).get("directors", [])
            if isinstance(root_directors, list):
                for director in root_directors:
                    if isinstance(director, dict):
                        director_data = {
                            "Id": director.get("id"),
                            "Full Name": director.get("fullName") 
                        }
                        director_list.append(director_data)

            output = {
                "Title": result.get("productModel", {}).get("title"),
                "Id": result.get("productModel", {}).get("id"),
                "Description": result.get("productModel", {}).get("description"),
                "Production date": result.get("productModel", {}).get("productionDate"),
                "Persons": persons_list,
                "Duration in minutes": duration_min,
                "Directors": director_list
            }

            json_out = json.dumps(output, ensure_ascii=False, indent=4)
            print(json_out)

            return output
        else:
            raise RuntimeError(f"Failed to fetch the item: {response.status_code}")

    def get_items(self, carousels: List[str]) -> List[int]:
        item_ids = []
        for carousel in carousels:
            response = requests.get(f'{HOST}/editorial/carousel?request=%7B%22id%22%3A%22{carousel}%22%2C%22pageNumber%22%3A1%2C%22pageSize%22%3A8%7D')
            if response.ok:
                result = response.json()
                total_count = result.get('count')
                page_size=result['pageSize']

                for page_number in range(0, (total_count//page_size)+1):
                    response = requests.get(f'{HOST}/editorial/carousel?request=%7B%22id%22%3A%22{carousel}%22%2C%22pageNumber%22%3A{page_number}%2C%22pageSize%22%3A8%7D')
                    if response.ok:
                        result = response.json()
                        if not result.get('editorialItems'):
                            break

                        for item in result.get('editorialItems', []):
                            item_data = self.get_item(item['item']['id'])
                            if item_data:  
                                item_ids.append(item['item']['id'])

        return item_ids

    def run(self):
        
        carousels = self.get_carousels()
        item_ids = self.get_items(carousels)
         


importer = ShahidMovieImporter(url='https://shahid.mbc.net/ar')
importer.run()
importer.get_items()

print()
