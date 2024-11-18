from collections import defaultdict 
from django.conf import settings 
import os 
import csv
from typing import List, Optional
from pydantic import BaseModel, Field

class CodedConcept(BaseModel):

    __hash__ = object.__hash__

    system: Optional[str] = Field(default=None)
    code: str = Field()
    display: Optional[str] = Field(default=None)
    definition: Optional[str] = Field(default=None)
    version: Optional[str] = Field(default=None)
    parent: Optional[str] = Field(default=None)
    synonyms: List[str] = Field(default=[])
    properties: Optional[dict] = Field(default=None)


def parse_OBO_file(file):
    """
    Parses a Gene Ontology dump in OBO v1.2 format.
    Yields each 
    Keyword arguments:
        filename: The filename to read
    """
    def process_OBO_term(goTerm):
        """
        In an object representing a GO term, replace single-element lists with
        their only member.
        Returns the modified object as a dictionary.
        """
        ret = dict(goTerm) #Input is a defaultdict, might express unexpected behaviour
        for key, value in ret.items():
            if len(value) == 1:
                ret[key] = value[0]
        return ret    
    
    currentGOTerm = None
    for line in file:
        line = line.strip()
        if not line: continue #Skip empty
        if line == "[Term]":
            if currentGOTerm: yield process_OBO_term(currentGOTerm)
            currentGOTerm = defaultdict(list)
        elif line == "[Typedef]":
            #Skip [Typedef sections]
            currentGOTerm = None
        else: #Not [Term]
            #Only process if we're inside a [Term] environment
            if currentGOTerm is None: continue
            key, sep, val = line.partition(":")
            currentGOTerm[key].append(val.strip())
    #Add last term
    if currentGOTerm is not None:
        yield process_OBO_term(currentGOTerm)

def get_dictreader_and_size(file, has_header=True, verbose=True):
    # Handle special OBO files
    if file.name.endswith('.obo'):
        reader = list(parse_OBO_file(file))
        total = len(reader)
        return reader, total 
    # Otherwise, handle the typical CSV/TSV files
    if verbose: print(f'• Loading file "{file.name}"...', end='')
    reader = csv.DictReader(file, delimiter="," if file.name.endswith('.csv') else '\t')
    if has_header:
        # Skip header
        next(reader)
    # Get number of rows
    total = len(list(reader))
    # Return to start of file
    file.seek(0)
    if has_header:
        # Skip header, agaom
        next(reader)
    if verbose:
        print(f' complete.')
        print(f'• Found {total} entries')
    return reader, total 

def get_file_location(path, filepart):
    DATA_PATH = os.path.join(settings.BASE_DIR, 'terminologyServer/terminologies/external/')
    # Work directory
    full_path = os.path.join(DATA_PATH, path)
    # Search for a valid file    
    files = [i for i in os.listdir(full_path) if os.path.isfile(os.path.join(full_path,i)) and filepart in i]
    if files:
        filename = files[0]
    else: 
        raise FileNotFoundError(f'There is no *{filepart}* file in the {path} directory.')
    return os.path.join(full_path,filename)

def ensure_within_string_limits(string):
    if len(string)>2000:
        string = string[:2000]    
    return string

def ensure_list(val):
    if not isinstance(val, list):
        return [val]
    return val
