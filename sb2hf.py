"""
Takes and creates an HuggingFace repository
"""

import argparse
import json
import os
import shutil

from urlparser import URLReader


def write_repository(url_reader):
    output_folder = f"{url_reader.resource_name}"
    print(f"Saving repository to {output_folder}")
    if os.path.exists(output_folder):
        shutil.rmtree(output_folder)
    os.mkdir(output_folder)
    url_reader.download_file(to=output_folder)
    with open(f'{output_folder}/{url_reader.resource_name}_config.json', 'w') as f:
        config = {
            'url': url_reader.url,
            'homepage': url_reader.url,
            'resource_name': url_reader.resource_name,
            'description': None,
            'citation': None
        }
        json.dump(config, f, indent=4, sort_keys=True)
        shutil.copyfile('hf_gen/dataset_loading_script.py', f'{output_folder}/{url_reader.resource_name}.py')


def sb2hf():
    url_reader = URLReader(args.url)
    write_repository(url_reader)    
    print("Finished. Now you just need to commit the repository to HuggingFace.")
    # TODO Create repository on HuggingFace programatically.


if __name__ == '__main__':
    parser = argparse.ArgumentParser(            
        prog='sb2hf',
        description='Creates a HuggingFace repository from an existing SB resource')
    parser.add_argument('url', help='URL to SB resource file (usually xml)')
    parser.add_argument('--hf-output-folder', help='Where to locally save the resulting HuggingFace repository.')
    parser.add_argument('--push-to-hub', help='If activated, pushes generated repository directly to hub.')
    parser.add_argument(
        '-r', '--row-output',
        choices=['sentences', 'tokens'], 
        help='Which output the rows should be in.'
    )
    args = parser.parse_args()
    if args.hf_output_folder is None:
        args.hf_output_folder = args.url.split('/')[-1]
    test = sb2hf()