"""
xls_to_schema1_yml converts an XLS file to a JSON structure with minor
modifications

* "select_one xyz" split to 2 columns
* "list name" changed to "list_name"

"""
import os
from pyxform import xls2json

def parse_xlsform(pth):
    xlspth = os.path.abspath(pth)
    return {
        **xls2json.xls_to_dict(xlspth),
        'schema': 'xlsform',
    }
