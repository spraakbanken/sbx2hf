"""

sb2hf.py

    A tool to automatically upload a Språkbanken resource to the Hugging Face Hub.

"""

import argparse
import json
import os
import logging
import shutil
import requests

import pandas as pd

from huggingface_hub import create_repo, HfApi, login, whoami

from helpers import get_bibtex_from_doi, get_value
from hf_gen.create_docs import write_readme
from hf_gen.dataloader import load_corpus_file
from urlparser import URLReader


def write_repository(url_reader):
    output_folder = f"{url_reader.resource_name}"
    print(f"Saving repository to {output_folder}")
    if os.path.exists(output_folder):
        shutil.rmtree(output_folder)
    os.mkdir(output_folder)
    metadata_query = f"{args.sbx_metadata_api}/metadata?resource={url_reader.resource_name}"
    logging.info(f"Fetching metadata from {metadata_query}")
    metadata = requests.get(metadata_query).json()
    write_readme(url_reader, metadata, f'{output_folder}/README.md')
    if args.upload_data:
        url_reader.download_file(to=output_folder)
        resource_fp = f'{output_folder}/{url_reader.bz2_local_path}'
        tsv_fp = f'{output_folder}/all.tsv'
        print(f"Converting {resource_fp} -> {tsv_fp}")
        pd.DataFrame(load_corpus_file(resource_fp), columns = ['text', 'id']).to_csv(tsv_fp, sep='\t')
        os.remove(resource_fp)
    else:
        with open(f'{output_folder}/{url_reader.resource_name}_config.json', 'w') as f:
            desc = get_value(metadata, 'description')
            config = {
                'url': url_reader.url,
                'homepage': url_reader.url,
                'resource_name': url_reader.resource_name,
                'description': desc,
                'citation': get_bibtex_from_doi(metadata['doi']).decode("utf-8")
            }
            json.dump(config, f, indent=4, sort_keys=True, ensure_ascii=False)
            shutil.copyfile('hf_gen/dataset_loading_script.py', f'{output_folder}/{url_reader.resource_name}.py')


def sb2hf():
    url_reader = URLReader(args.url)
    write_repository(url_reader)
    if args.push_to_hub:
        if not args.hf_token:
            try:
                user_info = whoami()
                print(f"User is authenticated: {user_info['name']}")
            except Exception:
                try:
                    login()
                except Exception:
                    print("Could not authenticate user.")
        else:
            print("Using API token for authentication.")
        repo_id, repo_type = f"{args.hf_namespace}/{url_reader.resource_name}", "dataset"
        create_repo(
            repo_id=repo_id,
            repo_type=repo_type,
            private= not args.hf_public,
            token=args.hf_token,
            exist_ok=True,
        )
        api = HfApi()
        api.upload_folder(
            folder_path=args.hf_output_folder,
            repo_id=repo_id,
            repo_type=repo_type,
        )
    else:
        print("Finished. Now you just need to upload the repository to HuggingFace.")


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        prog='sb2hf',
        description='Creates a HuggingFace repository from an existing SB resource')
    parser.add_argument('url', help='URL to resource page')
    parser.add_argument('--hf-output-folder', help="Where to locally save the resulting HuggingFace repository.")
    parser.add_argument('--push-to-hub', help="If activated, pushes generated repository directly to hub.", action='store_true', default=False)
    parser.add_argument('--hf-namespace', help="Huggingface user or organization to push dataset to", default='sbx')
    parser.add_argument('--hf-public', help="Flag if Hugging Face repository should be public", default=False)
    parser.add_argument('--hf-token', help="Huggingface User Access Token to authenticate to the Hub", default=os.environ.get('HF_TOKEN', None))
    parser.add_argument('--sbx-metadata-api', help="API back-end to fetch information about SBX resources", default="https://ws.spraakbanken.gu.se/ws")
    parser.add_argument('--upload-data',
                        help="""If set to True, the data (XML and JSON)
                                are uploaded to HuggingFace and uses the automated. Otherwise a
                                dataset loading script is uploaded which converts the data in
                                real time."""
                        , default=True)
    parser.add_argument( '-log',
                     '--loglevel',
                     default='warning',
                     help='Provide logging level. Example --loglevel debug, default=warning' )
    parser.add_argument(
        '-r', '--row-output',
        choices=['sentences', 'tokens'], 
        help='Which output the rows should be in.'
    )
    args = parser.parse_args()
    logging.basicConfig( level=args.loglevel.upper() )
    if args.hf_token and args.push_to_hub is None:
        parser.error("--hf-token requires --push-to-hub")
    if args.hf_output_folder is None:
        args.hf_output_folder = args.url.split('/')[-1]
    sb2hf()