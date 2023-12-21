###################################################################################################
#                                                                                                 #
#                                           DATALOADERS                                           #
#                                      for the SBX 2 HF repo                                      #
#                                                                                                 #
###################################################################################################


# Package Imports
import sys
import bz2

# Subpackage Imports
from bs4 import BeautifulSoup

# Aliased Imports
import xml.etree.ElementTree as ET


###################################################################################################

def load_xml( F: str | bz2.BZ2File ) -> list[str] :
    """
    This function takes in an XLM file in the new format (as of 2023) and ouputs its text.

    INPUT

     - F        An argument that determines where the XLM file can be read from. It can be either a
                string determining the path of the file or a bz2 file opened using bz2.open.

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


    for event, element in etree:

        # Load the sentences
        if event == "end" and element.tag == "token":
            sentence.append(element.text + element.attrib.get("_tail", " ")\
                                      .replace("\s", " ").replace(r"\n", " ").replace(r"\t", "\t"))
            element.clear()

        # If we find an end tag, we store the sentence and start a new one
        elif event == "end" and element.tag == "sentence":
            current_sentence = "".join(sentence)
            yield current_sentence
            sentence = []
            counter += 1

###################################################################################################

def load_corpus_file( path: str ) -> list[str] :
    """
    This function takes in either an XLM or a BZ2 file in the SBnew format (as of 2023) and ouputs
    its text.

    INPUT

     - path     A string that determines where the file can be read from.

    OUTPUT

        A generator that yields the sentences
    """

    # Automatically (and lazily) identify the extension of the file
    extension  = path.split(".")[-1]
    extension2 = path.split(".")[-2]

    print(extension2)

    # If we have an xml, extract the text from it
    if extension == "xml":
        while True:
            yield next( load_xml( F=path  ) )
    
    # If we have an xml.bz2 file, decompress and extract the text from it
    elif (extension == "bz2") and (extension2 == "xml"):
        with bz2.open(path, mode="r") as F:
            while True:
                yield next( load_xml( F=F ) )

    # Otherwise, raise an error
    else:
        raise NotImplementedError("Extension type "+extension+" is not supported at the time.")