#!usr/bin/env python3
from wiki_scraper import wiki_scraper
from gitHandler import gitHub

import wikipedia
from zipfile import ZipFile
import os
import json
from git import Repo
import multiprocessing as mp
import requests
import time

class build_json:
    def __init__(self, topic : str):
        # Combine 20th and 21st century actress lists
        self.wiki = wiki_scraper()

        self.wiki.loadData()
        self.data = self.wiki.wiki_data
        
        self.wiki.loadData("Category:21st-century_American_actresses")
        self.data.extend(self.wiki.wiki_data)
        
        self.topic = topic        
    
    # Make a request to the MediaWiki Api to get the first image link on the wiki page
    def getImageLink(self, names : str, index: int):
        session = requests.session()

        url = "https://en.wikipedia.org/w/api.php"

        params = {
            "action": "query",
            "format": "json",
            "list": "allimages",
            "aifrom": "",
            "ailimit": "1"
        }

        links = {}

        for name in names:
            params["aifrom"] = name
            res = session.get(url=url, params=params)
            data = res.json()

            link = data["query"]["allimages"]
            if link:
                links.update({name : link[0]["url"]})

        with open("imageLinks{}.json".format(index), "w") as f:
            f.write(json.dumps(links))
    
    # To split up work into 4 cores for reduced time
    def processing(self):
        names = [person["title"] for person in self.data]
        processes = []
        for index, piece in enumerate([names[i*(len(names) // 4):(i + 1)*(len(names) // 4)] for i in range(4)]):
            p = mp.Process(target = self.getImageLink, args = (piece, index))
            processes.append(p)
            p.start()
        for process in processes:
            process.join()


    # Build and write the json to images.json
    def download(self):
        print(len(self.data))
        images = {
                "info" : ["name"],
                self.topic : []
        }

        names = [person["title"] for person in self.data]
        
        fps = {}
        for i in range(4):
            linkfile = "imageLinks{}.json".format(i)
            with open(linkfile, "r") as f:
                fps.update(json.load(f))
            os.remove(linkfile)

        
        for person in self.data: 
            if person["title"] in fps:
                body = {}
                body.update({"name" : person["title"]})
                body.update({"filepath" : fps[person["title"]]})
                
                images[self.topic].append(body)
        print(images)
        savepath = os.path.join(os.getcwd(), "downloads/{}".format(self.topic))
        if not os.path.exists(savepath):
            os.mkdir(savepath)

        with open("downloads/{}/images.json".format(self.topic), "w") as f:
            f.write(json.dumps(images))
    
    # Helper function to get all file names in a directory
    def get_filepaths(self, directory : str) -> list:
        
        filepaths = []
        for root, directories, files in os.walk(directory):
            for filename in files:
                filepaths.append(filename)
        return filepaths
    
    # Zip the images to the quiqui_imgs repo
    def zip_downloaded_images(self):
        directory = "./downloads/" + self.topic

        filepaths = self.get_filepaths(directory)
        workingdir = os.getcwd()
        # print(workingdir)
        os.chdir(workingdir + f"/downloads/{self.topic}")
        with ZipFile(workingdir + f"/quiqui_imgs/{self.topic}.zip", "w") as zipfile:
            for filename in filepaths:
                zipfile.write(filename)

# Just run this code if this file is executed
if __name__ == "__main__":
    topic = "actresses"

    # Build the json    
    jsonobj = build_json(topic)
    jsonobj.processing()
    jsonobj.download()
    jsonobj.zip_downloaded_images()
    
    # Push to github
    gitHandler = gitHub("https://github.com/dhrumilp15/quiqui_imgs.git")
    gitHandler.push_to_github()