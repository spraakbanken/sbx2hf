"""
Takes and creates an HuggingFace repository
"""

import argparse



def sb2hf():
    raise NotImplementedError

if __name__ == '__main__':
    parser = argparse.ArgumentParser(            
        prog='sb2hf',
        description='Creates an HuggingFace repository from an existing SB resource')
    resource_filename = parser.add_argument('filename', help='SB resource file (usually xml)')
    parser.add_argument(
        '-r', '--row-output', 
        choices=['sentences', 'tokens'], 
        help='Which output the rows should be in.'
    )
    sb2hf()