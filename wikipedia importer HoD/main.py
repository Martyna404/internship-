
import argparse
from datetime import datetime
import locale
import os
from lxml import html, etree
import numpy as np
import pandas as pd
import requests
import re
from typing import  Dict
from typing import List
import json
import unicodedata

from lxml import html


class WikipediaImporter():

    SUPPORTED_LANGUAGES = ['fr','es','pt','pl','en','nl','hu','ru','tr','ro','sk']


    MAPPING_INFOBOX_XPATH= [
        '//table[contains(@class,"infobox")]',
        '//div[contains(@class,"infobox")]',
        '//table[contains(@class,"infocaseta")]'
    ]
    
    
    DATE_REGEX= [
        r'(\w+) \d{1,2}. \d{4}',
        r'\d{1,2} [a-zA-Z]+ \d{4}',    
        r'(\d{1,2}) [a-z]+ (\w+) [a-z]+ (\d{4})', 
        r'(\d{1,2}.) [a-zA-Z]+. (\d{4})',
        r'\d{4}. \w* \d{2}',
        r'\d{2} [А-Яа-яЁё]* \d{4}',
        r'\d{2} [a-zA-Z0-9ğüşöçİĞÜŞÖÇ]* \d{4}'     

    ]
 
 
    
    MAPPING_DIRECTORS={
        'pl':{
            'label': 'Reżyseria',
        },
        'es' : {
            'label': 'Dirigido por',
        },
        'pt' :{
            'label': 'Produtor(es) executivo(s)',
        },
        'nl':{
            'label': 'Regie',
        },
        'en':{
            'label': 'Showrunners',
        },
        'hu': {
            "label" : 'Rendező'
        },
        'ru' : {
            'label' : 'Режиссёр'
        },
        'tr' : {
            'label' : 'Geliştiren'
        },
        'ro' : {
            'label' : 'Regizor(i)'
        },
        'sk' : {
            'label' : 'Výkonný producent'
        }
    }


    MAPPING_DATE = {
        'pt': {
            'locale': 'pt_PT.UTF-8',
            'format': '%d de %B de %Y',
            'label': 'Transmissão original',

        },
        'pl': {
            'locale': 'pl_PL.UTF-8',
            'format': '%d %B %Y',
            'label': 'Data premiery',
   
        },
        'es': {
            'locale': 'es_ES.UTF-8',
            'format': '%d de %B de %Y',
            'label': 'Fecha de lanzamiento',

        },
        'fr': {
            'locale': 'fr_FR.UTF-8',
            'format': '%d %B %Y',
            'label': 'Diff. originale',
      
        },
        'en': {
            'locale': 'en_US.UTF-8',
            'format': '%Y-%m-%d',
            'label': 'Release',
 
        },
        'nl':{
            'locale': 'nl_NL.UTF-8',
            'format': '%d %B %Y',
            'label': 'Start',
        
        },
        'hu':{
            'locale': 'hu_HU.UTF-8',
            'format': '%Y. %B %d.',
            'label': 'Eredeti sugárzás',
        },
        'ru':{
            'locale': 'tu_RU.UTF-8',
            'format': '%Y. %B %d.',
            'label': 'Трансляция',
        },
        'tr' : {
            'locale': 'tr_TR.UTF-8',
            'format': '%Y. %B %d.',
            'label': 'Yayın tarihi',
        },
         'ro' : {
            'locale': 'ro_RO.UTF-8',
            'format': '%Y. %B %d.',
            'label': 'Perioadă de difuzare',
        },
        'sk' : {
            'locale': 'tr_TR.UTF-8',
            'format': '%Y. %B %d.',
            'label': 'Pôvodné',
        },
        
    
    }

    MAPPING_CAST = {
        'fr' : {
            'label': 'Acteurs principaux',
        },
        'es' : {
            'label': 'Protagonistas',

        },
        'pt' :{
            'label': 'Elenco',

        },
        'pl':{
            'label': 'role',

        },
        'nl':{
            'label': 'Hoofdrollen',

        },
        'en':{
            'label': 'Starring',
        },
        'hu':{
            'label': 'Főszereplő',
        },
        'ru':{
            'label' : 'В главных ролях'
        },
        'tr':{
            'label' : 'Başrol'
        },
        'ro':{
            'label' : 'Actori'
        },
        

    }
        
    MAPPING_EPISODES = {
        'en': {
            'xpath': '//table/tbody//tr//th[contains(text(),"Original air date")]/../../..',
            'indexes' : [1,2,3,5], 
        },
        'pl': {
            'xpath': '//table/tbody//tr//td//span//b[contains(text(),"Tytuł oryginalny")]/../../../../..',
            'indexes' : [1,2,3,5], 
        }

    }

    NAME_OF_EPISODES_TABLE={
        'en':{
                'magic_word':'Original air date'
        }
    }

    @staticmethod
    def fr_fun(arg):
        episodes = []
        result = []
        r = []
        regex = r'\((.*)\)'
        r1 = []
        for i in arg:
            p = ''.join(i.itertext())
            episodes.append(p)
        for j in episodes:
            result.append(j.split('\n'))

        for i in result:
            for j in i:
                j = re.search(r'\((.*)\)',j).group(0).strip("()")
                r.append(j)
            r1.append(r)
        return result
    
    """LF (character : \n, Unicode : U+000A, ASCII : 10, hex : 0x0a): This is simply the '\n' character which we all know from our early programming days. This character is commonly known as the ‘Line Feed’ or ‘Newline Character’.

CR (character : \r, Unicode : U+000D, ASCII : 13, hex : 0x0d) : This is simply the 'r' character. This character is commonly known as ‘Carriage Return’.
    """

    page: str


    def __init__(self, url: str, lang: str | None = None):
        self.lang = lang or WikipediaImporter.extract_language_from_url(url)
        self.url = url
        if self.lang not in self.SUPPORTED_LANGUAGES:
            raise RuntimeError(f"Language '{self.lang}' isn't supported by WikipediaImporter.")
   
 
    @staticmethod
    def extract_language_from_url(url):
        match = re.search(r'https?://([a-z]{2})\.wikipedia\.org', url)
        return match.group(1) if match else None
   
    def fetch_page_content(self):
        response = requests.get(self.url)
        if response.status_code == 200:
            self.page = response.text
            return response.text
        else:
            raise RuntimeError(f"Failed to fetch the page: {response.status_code}")
       
   
    def get_title(self):
        tree = html.fromstring(self.page)
        if self.lang in self.SUPPORTED_LANGUAGES:
            script_content = tree.xpath('//script/text()') 
            if script_content:
                script_text = script_content[0]
                rlconf_match = re.search(r'RLCONF\s*=\s*({.*?});', script_text, re.S)
            if rlconf_match:
                rlconf_text = rlconf_match.group(1)
                rlconf = json.loads(rlconf_text)
            return rlconf['wgTitle']
        raise ValueError('Didnt find the title')
       
              
    def get_infobox_value(self, label: str, group_obs: str | None = None, text: bool = True):
        tree = html.fromstring(self.page)
        if self.lang in self.SUPPORTED_LANGUAGES:
            for i in self.MAPPING_INFOBOX_XPATH:
                if len(tree.xpath(i))!=0:
                    infobox = tree.xpath(i)
                    if text:
                        value = "".join(infobox[0].xpath(f'.//tbody//tr[contains(.,"{label}")]//td//text()'))
                        return value
                    else:
                        value = infobox[0].xpath(f'.//tbody//tr[contains(.,"{label}")]/td')
                        if len(value) == 2:
                            return value[1]
                        return value[0]
            raise RuntimeError('infobox error')

            
    
    def get_directors(self):
        out_directors = []


        if self.lang in self.MAPPING_DIRECTORS:
            director_info = self.MAPPING_DIRECTORS[self.lang]
            directors =  self.get_infobox_value(director_info['label'],text = False)
            for i in directors.xpath('descendant::text()'):
                if len(i.strip())!=0 and i.istitle():
                    out_directors.append(i.strip())
            return out_directors
            

    def get_year(self):
        out_date = ""
        if self.lang in self.SUPPORTED_LANGUAGES:
            date_info = self.MAPPING_DATE[self.lang]
            date =  self.get_infobox_value(date_info['label'],text = True)
            for rgx in self.DATE_REGEX:
                if re.search(rgx, date.strip()):
                    out_date =  re.search(rgx, date.strip()).group(0)
        return out_date

    def get_cast(self):
        out_cast = []
        if self.lang in self.SUPPORTED_LANGUAGES:
            mapping = self.MAPPING_CAST[self.lang]
            cast = self.get_infobox_value(mapping['label'],text=False)
            for i in cast.xpath('descendant::text()'):
                if len(i.strip())!=0 and i.istitle():
                    out_cast.append(i.strip())
        return out_cast
        
    def get_episodes(self):
        episodes = []
        tree = html.fromstring(self.page.replace('<abbr title="Number">No.</abbr> in<br>season', 'No. in season'))
        tree = tree.xpath(self.MAPPING_EPISODES[self.lang]['xpath'])
        for i in tree:
            tree_str = etree.tostring(i,method="html")    #drzewo html na string 
            table = pd.read_html(tree_str)
            for t in table:
                t.dropna()
                for i in t._values:
                    episodes.append(i.tolist()) 
            print(tree_str)
        for x in episodes:
            pass
        
         
        
        return episodes


    def get_html_lang(self):
        match = re.search(r'lang=.([a-z]{2})',self.page)
        return match.group(1)

    def run(self): 
        importer.fetch_page_content()
# ============================================================

parser = argparse.ArgumentParser()
parser.add_argument("--url", type=str, help="The URL to be processed")
args = parser.parse_args()


importer = WikipediaImporter(url = 'https://sk.wikipedia.org/wiki/Rod_draka')
importer.run()   



importer.get_directors()









print()
