import os
import json
import argparse

from pyxform import xls2json
from pprint import pprint

from ..content import Content
from ..utils.form_to_yaml_string import form_to_yaml_string


def sans_headers_and_no_directional_quotes(pyxform_dict):
    delkeys = []
    for key in pyxform_dict.keys():
        if key.endswith('_header'):
            delkeys.append(key)
    for key in delkeys:
        del pyxform_dict[key]
    return json.loads(
        json.dumps(pyxform_dict).replace(
            '\\u201c', '\\"'
        ).replace(
            '\\u201d', '\\"'
        ).replace(
            '\\u2018', "'"
        ).replace(
            '\\u2019', "'"
        ).replace(
            '"TRUE"', 'true'
        ).replace(
            '"FALSE"', 'false'
        )
    )

def open_xls(path_in):
    xlspth = os.path.abspath(path_in)
    return {
        **sans_headers_and_no_directional_quotes(xls2json.xls_to_dict(xlspth)),
        'schema': 'xlsform',
    }

def print_out(form, validate=False, format=None):
    loaded_form = Content(form, validate=validate).export(schema='2')

    if format == 'json':
        print(json.dumps(loaded_form, indent=2))
    elif format == 'yml':
        print(form_to_yaml_string(loaded_form))

def run(path_in, path_out=None, validate=False, format=None):
    if not os.path.exists(path_in):
        raise ValueError('Path does not exist: ' + path_in)
    (pth, ext) = os.path.splitext(path_in)
    if ext in ['.xlsx', '.xls']:
        frm = open_xls(path_in)
    elif ext in ['yml']:
        frm = open_yml(path_in)
    elif ext in ['json']:
        frm = open_json(path_in)
    if path_out is None:
        print_out(frm, validate=validate, format=format)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        'path_in',
        help="Path to the YML file with the form definition",
    )
    parser.add_argument(
        '-o', '--output', dest='path_out',
        help='run the form through the schema validator',
    )
    parser.add_argument(
        '-f', '--format', dest='format',
        default='yml',
        choices=['yml', 'json', 'xml'],
        help='output format',
    )
    parser.add_argument(
        '-v', '--validate', dest='validate',
        action='store_true',
        help='run the form through the schema validator',
    )
    run(**parser.parse_args().__dict__)

if __name__ == '__main__':
    main()
