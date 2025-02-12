"""
    A module to automatically generate a Hugging Face README for an SBX resource 

"""

import codecs
import importlib
import logging
import pathlib
import pkg_resources
import requests
import yaml

from jinja2 import Template

from helpers import get_value
from runconfig_parser import Config, ConfigFromURL


def _create_hf_metadata_yaml(metadata: dict):
    yaml_content = yaml.dump({
        'language': [l['code'] for l in metadata['languages']] if 'languages' in metadata else None,
        'pretty_name':  get_value(metadata, 'short_description')
        },
        allow_unicode=True
    )
    return f"---\n{yaml_content}---"


def write_readme(path_parser: Config, metadata : dict, fp : str):
    if isinstance(path_parser, ConfigFromURL):
        api_endpoint = path_parser.sbx2hf_args['sbx_metadata_api']
        bibtex_query = f"{api_endpoint}/metadata/bibtex?resource={path_parser.resource_name}&type={metadata['type']}"
        logging.info(f"Fetching bibtex from {bibtex_query}")
        try:
            resp = requests.get(bibtex_query)
            bibtex = resp.json()['bibtex']
        except requests.exceptions.HTTPError as err:
            logging.info("Bibtex could not be fetched from metadata API")
            logging.info(err)
            bibtex = "None"
    else:
        bibtex = "None"
    try:
        sbx2hf_version = pkg_resources.get_distribution('sbx2hf').version
    except importlib.metadata.PackageNotFoundError:
        sbx2hf_version = "Unknown"
    template_variables = {
        'description': get_value(metadata, 'description'),
        'title' : get_value(metadata, 'name'),
        'bibtex': bibtex,
        'url': path_parser.sbx2hf_args.get('url', 'None'),
        'sbx2hf_version': sbx2hf_version
    }
    current_folder = pathlib.Path(__file__).parent.resolve()
    with open(f'{current_folder}/README.md', 'r') as file:
        template = Template(file.read(),trim_blocks=True)
        rendered_file = template.render(**template_variables)
    hf_metadata = _create_hf_metadata_yaml(metadata)
    output_file = codecs.open(fp, "w", "utf-8")
    readme = f"{hf_metadata}\n{rendered_file}"
    output_file.write(readme)
    output_file.close()