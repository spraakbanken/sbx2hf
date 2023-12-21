"""
Takes and creates an HuggingFace repository
"""

import argparse
import json
import os
import shutil

from hf_gen.generate_config import generate_config

def sb2hf():
    output_folder = f"generated/{args.hf_output_folder}"
    print(f"Saving repository to {output_folder}")
    os.mkdir(output_folder)
    with open('sb_config.json', 'w') as f:
        config = generate_config(args.resource_url, args.row_output)
        json.dump(config, f)
        shutil.copyfile('hf_gen/dataset_loading_script.py', f'{output_folder}/dataset_loading_script.py')
    print("Finished. Now you just need to commit the repository to HuggingFace.")
    # TODO Create repository on HuggingFace programatically.


if __name__ == '__main__':
    parser = argparse.ArgumentParser(            
        prog='sb2hf',
        description='Creates an HuggingFace repository from an existing SB resource')
    parser.add_argument('url', help='URL to SB resource file (usually xml)')
    parser.add_argument('--hf-output-folder', help='Where to locally save the resulting HuggingFace repository.')
    parser.add_argument(
        '-r', '--row-output',
        choices=['sentences', 'tokens'], 
        help='Which output the rows should be in.'
    )
    args = parser.parse_args()
    sb2hf()