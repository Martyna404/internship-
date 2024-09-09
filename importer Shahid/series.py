import requests
import json
from typing import List
from urllib.parse import quote

class Proba:
    HOST = "https://api2.shahid.net/proxy/v2.1"
    
    def get_carousels(self):
        response = requests.get(f'{self.HOST}/editorial/page?request=%7B%22pageAlias%22:%22series%22,%22profileFolder%22:%22WW%22%7D', headers={'uuid':'WEB'})
        if response.ok:
            result = response.json()
            carousels_ids = result.get('carousels', []) 
            carousels = [] 
            for carousel_id in carousels_ids:
                carousel = carousel_id.get('id') 
                encoded_carousel = quote(carousel)
                if carousel:
                    carousels.append(encoded_carousel)
                    
            return carousels 

    def get_all_serie(self, carousels: List[str]) -> List[int]:
        item_ids = []
        for encoded_carousel in carousels:
            response = requests.get(f'{self.HOST}/editorial/carousel?request=%7B%22id%22:%22{encoded_carousel}%22,%22pageNumber%22:0,%22pageSize%22:8,%22totalItems%22:48,%22displayedItems%22:0,%22itemsRequestedStatic%22:true%7D')
            if response.ok:
                result = response.json()
                total_count = result['count']
                page_size = result['pageSize']

                for page_number in range(0, (total_count // page_size) + 1):
                    page_response = requests.get(f'{self.HOST}/editorial/carousel?request=%7B%22id%22:%22{encoded_carousel}%22,%22pageNumber%22:{page_number},%22pageSize%22:8,%22totalItems%22:48,%22displayedItems%22:0,%22itemsRequestedStatic%22:true%7D')
                    if page_response.ok:
                        page_result = page_response.json()
                        editorial_items = page_result.get('editorialItems', [])   
                        for item in editorial_items:
                            serie_id1 = item.get('item', {}).get('seasons', [])
                            for item in serie_id1:
                                serie_id = item.get('id')
                                if serie_id:
                                    item_ids.append(serie_id)

        return item_ids

    def get_serie(self, serie_id: int):
        response = requests.get(f'{self.HOST}/playableAsset?request=%7B"seasonId"%3A"{serie_id}"%7D')
        if response.ok:
            result = response.json()
            root_seasons = result.get('productModel', {}).get('show', {}).get('seasons', [])
            seasons_data = []
            season_episodes = {}
            root_series = result.get('productModel', {}).get('show', {}).get('id')
            root_serie_title = result.get('productModel', {}).get('show', {}).get('title')
            root_serie_description = result.get('productModel', {}).get('show', {}).get('description')

            for season in root_seasons:
                season_id = season.get('id')
                season_title = season.get('title')
                season_number = season.get('seasonNumber')
                seasons_data.append({
                    "serie_id": root_series,
                    "serie_title": root_serie_title,
                    "serie_description": root_serie_description,
                    'season_id': season_id,
                    'season_title': season_title,
                    'season_number': season_number
                })

                season_response = requests.get(f'{self.HOST}/playableAsset?request=%7B"seasonId"%3A"{season_id}"%7D')
                if season_response.ok:
                    season_result = season_response.json()
                    root_play = season_result.get('productModel', {}).get('playlist', {})
                    play_list_id = root_play.get('id')
                    if play_list_id:
                        episodes = []
                        playlist_response = requests.get(f'{self.HOST}/product/playlist?request=%7B%22pageNumber%22%3A0%2C%22pageSize%22%3A6%2C%22playListId%22%3A{play_list_id}%2C%22sorts%22%3A%5B%7B%22order%22%3A%22DESC%22%2C%22type%22%3A%22SORTDATE%22%7D%5D%2C%22isDynamicPlaylist%22%3Afalse%7D')
                        if playlist_response.ok:
                            page_result = playlist_response.json()
                            products = page_result.get("productList", {}).get("products", [])
                                    
                            for product in products:
                                product_id = product.get("id")
                                persons = product.get('persons', [])
                                directors = product.get('directors', [])
                                root_duration = product.get('duration')
                                duration_min = root_duration / 60
                                comma = round(duration_min, 1)

                                persons_list = []
                                directors_list = []
                                
                                for person in persons:
                                    person_data = {
                                        "Id": person.get("id"),
                                        "name": person.get("fullName")
                                    }
                                    persons_list.append(person_data)

                                for director in directors:
                                    director_data = {
                                        'Id': director.get('id'),
                                        "name": director.get("fullName")
                                    }
                                    directors_list.append(director_data)
                                    
                                episodes.append({
                                    "episode_id": product_id,
                                    'persons': persons_list,
                                    "duration(minutes)": comma
                                })
 
                        season_episodes[season_id] = episodes

            final_output = []
            for season in seasons_data:
                season_id = season['season_id']
                season_info = {
                    "serie_id": season['serie_id'],
                    "serie_title": season['serie_title'],
                    "serie_description": season['serie_description'],
                    'season_id': season['season_id'],
                    'season_title': season['season_title'],
                    'season_number': season['season_number'],
                    'episodes': season_episodes.get(season_id, [])
                }
                final_output.append(season_info)

            json_out_series = json.dumps(final_output, ensure_ascii=False, indent=4)
            print(json_out_series)
                
            return final_output
        else:
            print("Failed")
            return None


my_instance = Proba()

carousels = my_instance.get_carousels()


series_ids = my_instance.get_all_serie(carousels)


for series_id in series_ids:
    my_instance.get_serie(series_id)
