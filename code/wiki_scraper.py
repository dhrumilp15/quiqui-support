#!/usr/bin/env python3
import sys
import requests

from info_handler import info_handler

input = sys.stdin.readline

BASE_URL = "https://en.wikipedia.org/w/api.php"

# Assume English wikipedia for now
PARAMS = {
    "action" : "query",
    "cmtitle" : "Category:20th-century_American_actresses",
    "cmlimit" : "max",
    "list" : "categorymembers",
    "format" : "json"
}

class wiki_scraper(info_handler):
    def __init__(self):
        self.wiki_data = []
    
    def loadData(self, link = None):
        super()

        session = requests.Session()
        flag = True
        params = PARAMS
        if link:
            params["cmtitle"] = link
        
        res = session.get(
                url = BASE_URL,
                params = params
            )

        data = res.json()
        self.parseData(data)
        while flag:
            if "continue" in data:
                params.update({"cmcontinue" : data["continue"]["cmcontinue"]})
                # print(params)
            else:
                flag = False
            
            res = session.get(
                url = BASE_URL,
                params = params
            )

            data = res.json()
            self.parseData(data)
    
    def parseData(self, data, **kwargs):
        super()
        info = data["query"]["categorymembers"]
        for person in info:
            # print(person["title"])
            if not "Category:" in person["title"]:
                self.wiki_data.append(person)