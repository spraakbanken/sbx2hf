import requests

def get_bibtex_from_doi(doi: str):
    try:
        doi_backend = "https://api.datacite.org/dois/application/x-bibtex"
        response = requests.get(f"{doi_backend}/{doi}")
    except requests.exceptions.HTTPError as err:
        raise SystemExit(err)
    return response.content


def get_value(resource_info : dict, key : str):
    short_description = resource_info[key]
    print(short_description)
    if short_description.get('eng', None):
        return short_description['eng']
    elif short_description.get('swe', None):
        return short_description['swe']
    else:
        return None