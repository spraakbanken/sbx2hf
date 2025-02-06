import pandas as pd

from pathlib import Path

from hf_gen.dataloader import load_corpus_file


def _write_file(path, output_path):
    print(f"Converting {path} -> {output_path}")
    df = pd.DataFrame(load_corpus_file(path), columns = ['text', 'id'])
    df.to_csv(output_path, sep='\t')


def write_files(config):
    if config.sbx2hf_args.get('url'):
        output_folder = config.output_folder
        output_path = f'{output_folder}/all.tsv'
        _write_file(config.bz2_local_path, output_path)
    else:
        for fn in config.sbx2hf_args['paths']:
            assert fn.endswith('.xml.bz2') or fn.endswith('.xml')
            base_fn = Path(fn).stem.split('.')[0]
            output_folder = config.output_folder
            output_path = f'{output_folder}/{base_fn}.tsv'
            _write_file(fn, output_path)