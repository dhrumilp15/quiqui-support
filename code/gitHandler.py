from git import Repo
import os

class gitHub:
    def __init__(self, link):
        cloneUrl = os.path.basename(link)[0:-4]
        localRepopath = os.path.dirname(os.getcwd())
        if os.path.exists(os.path.join(os.path.dirname(os.getcwd()), cloneUrl)):
            self.repo = Repo.init(os.path.join(os.path.dirname(os.getcwd()), f"{cloneUrl}/.git"))
        else:
            self.repo = Repo.clone_from(link, os.path.join(os.path.dirname(os.getcwd()), cloneUrl), branch = "master")
    
    def push_to_github(self):
        self.repo.git.add(".")
        self.repo.index.commit("New Package!")
        origin = self.repo.remote("origin")
        origin.pull()
        origin.push()