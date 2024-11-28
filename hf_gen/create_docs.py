"""
    A module to automatically generate a Hugging Face README for an SBX resource 

"""

import codecs
import importlib
import logging
import pkg_resources
import requests
import yaml


from jinja2 import Template

from helpers import get_value
from urlparser import URLReader


def write_readme(url_reader: URLReader, metadata : dict, fp : str):
    TEMP_LINK = "https://ws.spraakbanken.gu.se/ws/metadata-dev/" # TODO: remove this when endpoint is in production 
    bibtex_query = f"{TEMP_LINK}/bibtex?resource={url_reader.resource_name}&type={metadata['type']}"
    logging.info(f"Fetching bibtex from {bibtex_query}")
    bibtex = requests.get(bibtex_query).json()['bibtex']
    try:
        sb2hf_version = pkg_resources.get_distribution('sb2hf').version
    except importlib.metadata.PackageNotFoundError:
        sb2hf_version = "Unknown"
    template_variables = {
        'description': get_value(metadata, 'description'),
        'title' : get_value(metadata, 'name'),
        'bibtex': bibtex,
        'url': url_reader.url,
        'sb2hf_version': sb2hf_version
    }
    with open('hf_gen/README.md', 'r') as file:
        template = Template(file.read(),trim_blocks=True)
        rendered_file = template.render(**template_variables)
    #output the file
    hf_metadata = create_hf_metadata_yaml(metadata)
    output_file = codecs.open(fp, "w", "utf-8")
    readme = f"{hf_metadata}\n{rendered_file}"
    output_file.write(readme)
    output_file.close()

def create_hf_metadata_yaml(metadata: dict):
    yaml_content = yaml.dump({
        'language': [l['code'] for l in metadata['languages']],
        'pretty_name':  get_value(metadata, 'short_description')
        },
        allow_unicode=True
    )
    return f"---\n{yaml_content}---"