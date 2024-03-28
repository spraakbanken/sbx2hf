###################################################################################################
#                                                                                                 #
#                                           DATALOADERS                                           #
#                                      for the SBX 2 HF repo                                      #
#                                                                                                 #
###################################################################################################


# Package Imports
import sys

# Subpackage Imports
from bs4 import BeautifulSoup
from typing import Generator
from bz2 import BZ2File 

# Aliased Imports
import xml.etree.ElementTree as ET
#import lxml.etree as ET


###################################################################################################

def load_xml( F : str | BZ2File , keep_paragraphs : bool = True ) -> Generator :
    """
    This function takes in an XLM file in the new format (as of 2023) and ouputs its text.

    INPUT

     - F        An argument that determines where the XLM file can be read from. It can be either a
                string determining the path of the file or a bz2 file opened using bz2.open.

    - keep_paragraphs   A boolean that determines whether to return sentences separately or to
                        return them together.
                        default : True

    OUTPUT

        A generator that yields the sentences
    """

    # We got the original version of this function from Martin

    # Load the XLM tree
    etree = ET.iterparse(F, events=("end",))

    # Initialize variables
    sentence = []

    # Head counter
    counter = 0

    # TODO - use this to load old files(?)
    has_tails = False

    keep = ["token","w"]
    split = ["text","corpus"]
    sections = ["sentence","paragraph"]

    if keep_paragraphs:
        keep.extend(sections)
    else:
        split.extend(sections)

    for event, element in etree:

        # Load the sentences
        if event == "end" and element.tag.lower() in keep:
            sentence.append(element.text + element.attrib.get("_tail", " ")\
                                      .replace("\s", " ").replace(r"\n", " ").replace(r"\t", "\t"))
            element.clear()

        # If we find an end tag, we store the sentence and start a new one
        elif event == "end" and element.tag.lower() in split:
            current_sentence = "".join(sentence)
            yield current_sentence
            sentence = []
            counter += 1

        else:
            print(event, element.tag, element.text)
            raise Exception("I do not know how to parse this tag at the moment")

###################################################################################################

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

    #print(extension2)

    # If we have an xml, extract the text from it
    if extension == "xml":
        generator = load_xml( F=path , keep_paragraphs=keep_paragraphs )
        while True:
            yield next( generator )
    
    # If we have an xml.bz2 file, decompress and extract the text from it
    elif (extension == "bz2") and (extension2 == "xml"):
        with BZ2File(path, mode="r") as F:
            generator = load_xml( F=F , keep_paragraphs=keep_paragraphs )
            while True:
                yield next( generator )

    # Otherwise, raise an error
    else:
        raise NotImplementedError("Extension type "+extension+" is not supported at the time.")
    


###################################################################################################
