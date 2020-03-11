import requests
import json

class restbus:
    def __init__(self):
        '''The RestBus API setup'''
        self.base_url = 'http://restbus.info/api/agencies/sf-muni/'
        self.routes_url = 'routes/'
        self.vehicles_url = 'vehicles/'
        self.headers = {'Content-Type': 'application/json'}

    def get_json(self, content_url):

        s = requests.Session()
        s.headers.update(self.headers)
        url = self.base_url+content_url

        try:
            status = s.get(url).json()
            s.close()
        except:
            status = ""

        return status
