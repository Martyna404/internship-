import requests
import json

class AnimeImporter:
    def __init__(self):
        self.url = 'https://graphql.anilist.co'

    def get_item(self, page):
        query = '''
        query ($page: Int) {
            Page(page: $page) {
                pageInfo {
                    total
                    currentPage
                    lastPage
                    hasNextPage
                }
                media(type: ANIME) {
                    id
                    title {
                        romaji
                        english
                        native
                    }
                    description
                    siteUrl
                    characters {
                        edges {
                            node {
                                id
                                name {
                                    first
                                    last
                                    native
                                }
                            }
                            voiceActors {
                                id
                                name {
                                    first
                                    last
                                    native
                                }
                                language
                            }
                        }
                    }
                    staff {
                        edges {
                            node {
                                id
                                name {
                                    first
                                    last
                                    native
                                }
                            }
                            
                        }
                    }
                }
            }
        }
        '''
        variables = {
            'page': page
        }

        response = requests.post(self.url, json={'query': query, 'variables': variables})
        response.raise_for_status()
        return response.json()

    def get_items(self):
        all_anime = []
        page = 1
        data = self.get_item(page=page)
        last_page = data.get('data', {}).get('Page', {}).get('pageInfo', {}).get('lastPage')
        
        for page in range(1, last_page + 1):  
            data = self.get_item(page=page)
            media = data.get('data', {}).get('Page', {}).get('media', [])
            all_anime.extend(media)

            if len(all_anime) >= 10:
                break

        return all_anime[:1]
    
    # def search_director(self):
    #     lista=[]
    #     for anime in first_10_anime:
    #         lista.append(anime)
    #         return lista


def results(all_anime):
    for anime in enumerate(all_anime):
        formatted_json = json.dumps(anime, ensure_ascii=False, indent=4)
        print(formatted_json)



anime_importer = AnimeImporter()
first_10_anime = anime_importer.get_items()
results(first_10_anime) 
print() 
