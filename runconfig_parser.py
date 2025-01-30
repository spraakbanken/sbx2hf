"""
    Parses metadata and sbx2hf arguments to one Configuration class.
"""

import logging
import requests

from urllib.parse import urlsplit


def _fetch_metadata(api_endpoint : str, resource_name):
    metadata_query = f"{api_endpoint}/metadata?resource={resource_name}"
    logging.info(f"Fetching metadata from {metadata_query}")
    metadata = requests.get(metadata_query).json()
    return metadata


def create_runconfig(sbx2hf_args : dict):
    if sbx2hf_args['url']:
        resource_name = sbx2hf_args['url'].strip('/').split('/')[-1]
        metadata = _fetch_metadata(sbx2hf_args['sbx_metadata_api'], resource_name)
        return ConfigFromURL(sbx2hf_args, metadata)
    else:
        metadata = sbx2hf_args.get('metadata', {})
        return ConfigFromPaths(sbx2hf_args, metadata)


class Config():

    def __init__(self, sbx2hf_args : dict, metadata : dict):
        self.sbx2hf_args = sbx2hf_args
        self.metadata = metadata

    @property
    def resource_name(self):
        return self.metadata.get('id', 'None')
    
    @property
    def output_folder(self):
        if self.sbx2hf_args['hf_output_folder']:
            return self.sbx2hf_args['hf_output_folder']
        return self.resource_name


class ConfigFromPaths(Config):

    @property
    def datapaths(self):
        if self.path is not list:
            raise ValueError()
        return self.path


class ConfigFromURL(Config):

    @property
    def bz2link(self):
        split_path = urlsplit(self.sbx2hf_args['url'])
        return f'{split_path.scheme}://{split_path.netloc}/lb/resurser/meningsmangder/{self.resource_name}.xml.bz2'
    
    @property
    def bz2_local_path(self):
        return f'{self.output_folder}/{self.resource_name}.xml.bz2'

    def download_file(self, to : str = None):
        to = to if to else self.bz2_local_path
        logging.info(f"Downloading file {self.bz2link} file to {to}")
        with requests.get(self.bz2link, stream=True) as r:
            r.raise_for_status()
            with open(self.bz2_local_path, 'wb') as f:
                for chunk in r.iter_content(chunk_size=8192): 
                    f.write(chunk)
        return self.bz2_local_path