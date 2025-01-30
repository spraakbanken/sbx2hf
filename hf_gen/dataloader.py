"""

Dataloaders to convert from Språkbanken XML files to tabular json files

"""

from typing import Generator
from bz2 import BZ2File 

import xml.etree.ElementTree as ET

import requests


def load_xml( F : str | BZ2File | requests.Response, keep_paragraphs : bool = True ) -> Generator :
    """
    This function takes in an XLM file in the new format (as of 2023) and old format and ouputs its text.

    INPUT

     - F        An argument that determines where the XLM file can be read from. It can be either a
                string determining the path of the file or a bz2 file opened using bz2.open.

    - keep_paragraphs   A boolean that determines whether to return sentences separately or to
                        return them together.
                        default : True

    OUTPUT

        A generator that yields the sentences
    """

    # Parse the XML file
    tree = ET.parse(F)
    root = tree.getroot()

    # Extract corpus information
    corpus_id = root.attrib.get("id")
    print(f"Corpus ID: {corpus_id}")
    # Iterate through all sentences
    for sentence_idx, sentence in enumerate(root.iter("sentence")):
        sentence_id = sentence.attrib.get("id", sentence_idx)
        # Extract words in the sentence
        words = []
        for word in sentence.findall("w") + sentence.findall('token'):
            word_text = word.text
            words.append(word_text)
        sent = " ".join(words)
        yield sent, sentence_id
                



def load_corpus_file( path : str , keep_paragraphs : bool = True ) -> Generator :
    """
    This function takes in either an XLM or a BZ2 file in the SBnew format (as of 2023) and ouputs
    its text.

    INPUT

     - path     A string that determines where the file can be read from.

    - keep_paragraphs   A boolean that determines whether to return sentences separately or to
                        return them together.
                        default : True

    OUTPUT

        A generator that yields the sentences
    """

    # Automatically (and lazily) identify the extension of the file
    extension  = path.split(".")[-1]
    extension2 = path.split(".")[-2]

    # If we have an xml, extract the text from it
    if extension == "xml":
        generator = load_xml( F=path , keep_paragraphs=keep_paragraphs )
        for sent, sent_id in generator:
                yield sent, sent_id
    
    # If we have an xml.bz2 file, decompress and extract the text from it
    elif (extension == "bz2") and (extension2 == "xml"):
        with BZ2File(path, mode="r") as F:
            generator = load_xml( F=F , keep_paragraphs=keep_paragraphs )
            for sent, sent_id in generator:
                yield sent, sent_id

    # Otherwise, raise an error
    else:
        raise NotImplementedError("Extension type "+extension+" is not supported at the time.")