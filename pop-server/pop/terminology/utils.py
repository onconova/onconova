from collections import defaultdict 
import os 
import csv
import requests
from typing import List, Optional, TextIO, Tuple, Union
from pydantic import BaseModel, Field
import environ 

# Load environmental variables
env = environ.Env()
environ.Env.read_env('.env', overwrite=True)

_cache = {}

# Custom function to print with color
def printRed(skk): print("\033[91m {}\033[00m" .format(skk))
def printGreen(skk): print("\033[92m {}\033[00m" .format(skk))
def printYellow(skk): print("\033[93m {}\033[00m" .format(skk))

class CodedConcept(BaseModel):
    """
    Class representing a single concept in a codesystem.

    Attributes:
        system (str): The URL of the codesystem in which the concept is defined.
        code (str): The code for the concept in the codesystem.
        display (str): The human-readable name of the concept.
        definition (str): The formal definition of the concept.
        version (str): The version of the codesystem.
        parent (str): The code of the parent concept.
        synonyms (List[str]): A list of synonyms for the concept.
        properties (dict): A dictionary of additional properties for the concept.
    """


    system: Optional[str] = Field(default=None)
    code: str = Field()
    display: Optional[str] = Field(default=None)
    definition: Optional[str] = Field(default=None)
    version: Optional[str] = Field(default=None)
    parent: Optional[str] = Field(default=None)
    synonyms: List[str] = Field(default=[])
    properties: Optional[dict] = Field(default=None)

    def __hash__(self):
        return hash(self.__repr__())

def parent_to_children(codesystem: dict) -> dict:
    """
    Preprocesses the codesystem to create a mapping from parent codes to their children.

    This function takes in a codesystem as a dictionary where each value is a concept with `code` and `parent`
    attributes. It then creates a mapping from parent codes to their children (i.e., concepts that have the parent
    code as their `parent` attribute).

    Args:
        codesystem (dict): A dictionary where each value is a concept with `code` and `parent` attributes.

    Returns:
        dict: A dictionary mapping parent codes to a list of their child concepts.

    Notes:
        This function caches its results, so if it is called with the same codesystem multiple times, it will return
        the same result without recomputing it.
    """
    if id(codesystem) in _cache:
        return _cache[id(codesystem)]
    mapping = defaultdict(list)
    for concept in codesystem.values():
        mapping[concept.parent].append(concept)
    _cache[id(codesystem)] = mapping
    return mapping

from typing import Generator, Dict, Any
from collections import defaultdict



def parse_OBO_file(file) -> Generator[Dict[str, Any], None, None]:
    """
    Parses a Gene Ontology dump in OBO v1.2 format.

    Args:
        file: An iterable object that yields lines of text, representing an OBO file.

    Yields:
        dict: Each GO term as a dictionary with keys as term attributes and values
              as attributes' values, converting single-element lists to single values.
    """
    def process_OBO_term(goTerm: defaultdict) -> Dict[str, Any]:
        """
        In an object representing a GO term, replace single-element lists with
        their only member.

        Args:
            goTerm: A defaultdict representing a GO term with attributes as keys.

        Returns:
            dict: The modified object as a dictionary.
        """
        ret = dict(goTerm)  # Input is a defaultdict, might express unexpected behaviour
        for key, value in ret.items():
            if len(value) == 1:
                ret[key] = value[0]
        return ret    

    currentGOTerm = None
    for line in file:
        line = line.strip()
        if not line:
            continue  # Skip empty
        if line == "[Term]":
            if currentGOTerm:
                yield process_OBO_term(currentGOTerm)
            currentGOTerm = defaultdict(list)
        elif line == "[Typedef]":
            # Skip [Typedef] sections
            currentGOTerm = None
        else:  # Not [Term]
            # Only process if we're inside a [Term] environment
            if currentGOTerm is None:
                continue
            key, sep, val = line.partition(":")
            currentGOTerm[key].append(val.strip())
    # Add last term
    if currentGOTerm is not None:
        yield process_OBO_term(currentGOTerm)




def get_dictreader_and_size(file: TextIO, has_header: bool = True, verbose: bool = True) -> Tuple[List[Dict[str, str]], int]:
    """
    Get a DictReader for a file and the total number of rows. Accepts `.csv`, `.tsv`, and `.obo` files.

    Args:
        file (TextIO): The file to read from.
        has_header (bool, optional): True if the file has a header row. Defaults to True.
        verbose (bool, optional): True if progress should be printed. Defaults to True.

    Returns:
        Tuple[List[Dict[str, str]], int]: A tuple containing the DictReader (or list for OBO files) and the number of rows.

    Raises:
        ValueError: If the file format is not supported.
    """
    if verbose:
        print(f'• Loading file "{file.name}"...', end='')

    # Special case for OBO files
    if file.name.endswith('.obo'):
        # Parse the OBO file
        reader = list(parse_OBO_file(file))
        total = len(reader)
        return reader, total

    # Handle CSV/TSV files
    elif file.name.endswith('.csv') or file.name.endswith('.tsv'):
        # Determine the delimiter based on file extension
        delimiter = "," if file.name.endswith('.csv') else '\t'
        # Initialize the DictReader
        reader = csv.DictReader(file, delimiter=delimiter)
        if has_header:
            # Skip header if present
            next(reader)
        # Count the number of rows
        total = len(list(reader))
        # Reset file pointer to start
        file.seek(0)
        if has_header:
            # Skip header again after reset
            next(reader)

        if verbose:
            print(' complete.')
            print(f'• Found {total} entries')
        return reader, total

    else:
        # Raise an error for unsupported file formats
        raise ValueError('Invalid file format. Must be an `.csv`, `.tsv`, or `.obo` file.')



def get_file_location(path: str, filepart: str) -> str:
    """
    Get the file location by searching for a file containing the specified substring in its name.

    Args:
        path (str): The directory path to search in.
        filepart (str): The substring to search for in file names.

    Returns:
        str: The full path of the found file.

    Raises:
        FileNotFoundError: If no file containing the substring is found in the directory.
    """
    files = [i for i in os.listdir(path) if os.path.isfile(os.path.join(path, i)) and filepart in i]
    if files:
        filename = files[0]
    else:
        raise FileNotFoundError(f'There is no *{filepart}* file in the {path} directory.')
    return os.path.join(path, filename)


def ensure_within_string_limits(string: str) -> str:
    """
    Ensure that a given string is limited to 2000 characters or less.

    Args:
        string (str): The string to truncate.

    Returns:
        str: The string, truncated to 2000 characters or less.
    """
    if len(string)>2000:
        string = string[:2000]    
    return string


def ensure_list(val: Any) -> List[Any]:
    """
    Ensure that a given value is returned as a list.

    Args:
        val (Any): The value to be checked and converted into a list if necessary.

    Returns:
        List[Any]: A list containing the original value if it was not a list, otherwise the original list itself.
    """
    if not isinstance(val, list):
        return [val]
    return val


def request_http_get(api_url: str, raw: bool = False) -> Union[Dict[str, Any], str]:
    """
    Make a GET request to an API endpoint, parse the JSON response, and return the parsed JSON data.

    Args:
        api_url (str): The URL of the API endpoint to make the request to.
        raw (bool, optional): If True, return the raw response text instead of the parsed JSON data. Defaults to False.

    Returns:
        Union[Dict[str, Any], str]: The parsed JSON data if raw is False, otherwise the raw response text.

    Note:
        This function sets up the necessary configurations, including basic authentication,
        proxies, and certificate verification, to make a secure API request.
    """
    # Define the API endpoint basic authentication credentials
    if 'loinc.org' in api_url:
        api_username = env('LOINC_USER')
        api_password = env('LOINC_PASSWORD')
    elif 'nlm.nih.gov' in api_url:
        api_username = env('UMLS_API_USER')
        api_password = env('UMLS_API_KEY')
    else: 
        api_username, api_password = None, None

    # Define the path to the certificate bundle file
    certificate_bundle_path = env('CA_SSL_CERT_BUNDLE')

    # Create a session for making the request
    session = requests.Session()

    # Set up the proxy with authentication
    proxies = {
        'http': env('PROXY_HTTP'),
        'https': env('PROXY_HTTPS'),
    }
    session.proxies = proxies
    # Set up the basic authentication for the API
    if api_username and api_password:
        session.auth = (api_username, api_password)

    # Make a GET request to the API and parse the JSON response
    response = session.get(api_url, verify=certificate_bundle_path, proxies=proxies)

    # Check if there is an authorization issue
    if response.status_code == 401:
        # If authorization is required, the session cookies have now been set by the first request and a second request is necessary 
        response = session.get(api_url, verify=certificate_bundle_path, proxies=proxies)

    # Check for custom FHIR expansion response code
    if response.status_code == 422 and '$expand' in api_url:
        # If expansion operation is too costly, server will refuse, in that case, get non-expanded content definition
        response = session.get(api_url.replace('$expand',''), verify=certificate_bundle_path, proxies=proxies)

    # Check for unknown URL response code
    if response.status_code == 404 and 'mcode' in api_url.lower():
        # Certain mCODE valuesets use a different domain to serve the JSON representations
        response = session.get(api_url.replace("build.fhir.org/ig/HL7/fhir-mCODE-ig/", "hl7.org/fhir/us/mcode/"), verify=certificate_bundle_path, proxies=proxies)

    if response.status_code == 200:
        # Successfully connected to the API
        if raw:
            return response.text
        json_response = response.json()  # Parse JSON response
        # Now you can work with the JSON data
        return json_response
    else:
        printRed(f"NETWORK ERROR: Request failed with status code: {response.status_code}")
        response.raise_for_status()
        
