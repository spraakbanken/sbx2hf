"""
sb2hf.py

    A tool to automatically upload a Språkbanken resource to the Hugging Face Hub.
"""

import argparse
import json
import os
import logging
import shutil

from huggingface_hub import create_repo, HfApi, login, whoami

from runconfig_parser import ConfigFromURL, create_runconfig
from helpers import is_url, get_bibtex_from_doi, get_value
from hf_gen.create_docs import write_readme
from hf_gen.create_data_files import write_files


def write_repository(runconfig):
    output_folder = f"{runconfig.resource_name}"
    print(f"Saving repository to {output_folder}")
    if os.path.exists(output_folder):
        shutil.rmtree(output_folder)
    os.mkdir(output_folder)
    if not runconfig.sbx2hf_args['hf_dataloading_script']:
        if isinstance(runconfig, ConfigFromURL):
            runconfig.download_file(to=output_folder)
        write_files(runconfig)
    else:
        with open(f'{output_folder}/{runconfig.resource_name}_config.json', 'w') as f:
            desc = get_value(runconfig.metadata, 'description')
            runconfig = {
                'homepage': runconfig.resource_name,
                'resource_name': runconfig.resource_name,
                'description': desc,
                'citation': get_bibtex_from_doi(runconfig['metadata']['doi']).decode("utf-8")
            }
            json.dump(runconfig, f, indent=4, sort_keys=True, ensure_ascii=False)
            shutil.copyfile('hf_gen/dataset_loading_script.py', f'{output_folder}/{runconfig.resource_name}.py')
    write_readme(runconfig, runconfig.metadata, f'{output_folder}/README.md')


def sbx2hf(**sbx2hf_args):
    runconfig = create_runconfig(sbx2hf_args)
    write_repository(runconfig)
    if sbx2hf_args['push_to_hub']:
        if not sbx2hf_args['hf_token']:
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
        repo_id, repo_type = f"{sbx2hf_args['hf_namespace']}/{runconfig.resource_name}", "dataset"
        create_repo(
            repo_id=repo_id,
            repo_type=repo_type,
            private= not sbx2hf_args['hf_public'],
            token=sbx2hf_args['hf_token'],
            exist_ok=True,
        )
        api = HfApi()
        api.upload_folder(
            folder_path=runconfig['hf_output_folder'],
            repo_id=repo_id,
            repo_type=repo_type,
        )
    else:
        print("Finished. Now you just need to upload the repository to HuggingFace.")


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        prog='sb2hf',
        description="Creates a HuggingFace repository from an existing SBX resource or from Sparv .xml.bz2 file")

    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--url', help='URL to an SBX resource page.')
    group.add_argument('--paths', nargs='+', help='Paths to local Sparv .xml file(s)')

    parser.add_argument('--hf-output-folder', help="Where to locally save the resulting HuggingFace repository.")
    parser.add_argument('--push-to-hub', help="If activated, pushes generated repository directly to hub.", action='store_true', default=False)
    parser.add_argument('--hf-namespace', help="Huggingface user or organization to push dataset to", default='sbx')
    parser.add_argument('--hf-public', help="Flag if Hugging Face repository should be public", default=False)
    parser.add_argument('--hf-token', help="Huggingface User Access Token to authenticate to the Hub", default=os.environ.get('HF_TOKEN', None))
    parser.add_argument('--sbx-metadata-api', help="API back-end to fetch information about SBX resources", default="https://ws.spraakbanken.gu.se/ws")
    parser.add_argument('--hf-dataloading-script',
                        help="""If set to True, the data (XML and JSON)
                                are uploaded to HuggingFace and uses the automated scripts. Otherwise a
                                dataset loading script is uploaded which converts the data in
                                real time."""
                        , default=False)
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
    if args.url and not is_url(args.url):
        parser.error('--url is not a valid URL')
    if type(args.paths) == list and any(is_url(p) for p in args.paths):
        parser.error('--paths only accepts a list of local paths')
    if args.hf_token and args.push_to_hub is None:
        parser.error("--hf-token requires --push-to-hub")
    sbx2hf_args = vars(args)
    sbx2hf(**sbx2hf_args)