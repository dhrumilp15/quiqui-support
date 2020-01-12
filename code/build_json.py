from wiki_scraper import wiki_scraper

import wikipedia
from google_images_download import google_images_download
from zipfile import ZipFile
import os
import json
from git import Repo

class build_json:
    def __init__(self, topic):
        # Combine 20th and 21st century actress lists
        self.wiki = wiki_scraper()
        self.wiki.loadData()
        self.data = self.wiki.wiki_data
        self.wiki.loadData("Category:21st-century_American_actresses")
        self.data.extend(self.wiki.wiki_data)
        self.topic = topic
        
        self.res = google_images_download.googleimagesdownload()
        
        self.toZip = []
    
    def getImages(self, person):
        args = {
            "keywords" : person["title"],
            "limit" : 1,
            "size" : "medium",
            "aspect_ratio" : "square",
            "image_directory" : self.topic
            }
        try:
            paths = self.res.download(args)
            if paths[0][person["title"]]:
                filepath = paths[0][person["title"]][0]
                return filepath[filepath.rindex("/") + 1:]
            else:
                return False
        except:
            return False

    def build_json(self):
        print(len(self.data))
        images = {
                "info" : ["name"],
                self.topic : []
            }
        for person in self.data:            
            body = {}
            body.update({"name" : person["title"]})

            path = self.getImages(person)
            if path:
                body.update({"filepath" : path})
        
            images[self.topic].append(body)
        
        with open("downloads/images.json") as f:
            f.write(json.dumps(images))
        f.close()
    
    def get_filepaths(self, directory):
        
        filepaths = []
        for root, directories, files in os.walk(directory):
            for filename in files:
                filepath = os.path.join(root, filename)
                filepaths.append(filepath)
        
        return filepaths
    
    def zip_downloaded_images(self):
        directory = "./downloads/" + self.topic

        filepaths = self.get_filepaths(directory)

        with ZipFile(os.path.dirname(os.getcwd()) + "/packages/{}.zip".format(self.topic), "w") as zipfile:
            for filename in filepaths:
                zipfile.write(filename)

    def push_to_github(self):
        repo = Repo(os.path.dirname(os.getcwd()))

        with repo.config_reader():
            pass
        repo.git.add(update=True)
        repo.index.commit("New Package!")
        origin = repo.remote(name = 'origin')
        origin.push()

topic = "actresses"

build_json = build_json(topic)
# build_json.build_json()
# build_json.zip_downloaded_images()
build_json.push_to_github()