import requests

from typing import Dict
from urllib.parse import urlsplit

class URLReader:

    def __init__(self, url : str):
        self.url = url        

    @property
    def resource_name(self):
        return self.url.strip('/').split('/')[-1]
    
    @property
    def bz2link(self):
        split_url = urlsplit(self.url)
        return f'{split_url.scheme}://{split_url.netloc}/lb/resurser/meningsmangder/{self.resource_name}.xml.bz2'
    
    @property
    def bz2_local_path(self):
        return self.resource_name + '.xml.bz2'
    
    def download_file(self, to : str = ''):
        # NOTE the stream=True parameter below
        print(f"Downloading file {self.bz2link}")
        with requests.get(self.bz2link, stream=True) as r:
            r.raise_for_status()
            with open(f'{to}/{self.bz2_local_path}', 'wb') as f:
                for chunk in r.iter_content(chunk_size=8192): 
                    # If you have chunk encoded response uncomment if
                    # and set chunk_size parameter to None.
                    #if chunk: 
                    f.write(chunk)
        return self.bz2_local_path