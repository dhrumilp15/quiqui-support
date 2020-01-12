#!/usr/bin/env python3

from abc import ABC, abstractmethod

class info_handler(ABC):

    @abstractmethod
    def loadData(self):
        pass

    def parseData(self, **kwargs):
        pass