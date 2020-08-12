import os
import json
import yaml
import argparse

from pyxform import xls2json
from pyxform.builder import create_survey_element_from_dict

from pprint import pprint

from ..content_variations import build_content
from ..utils.form_to_yaml_string import form_to_yaml_string


YAML_FORMAT = 'yml'
JSON_FORMAT = 'json'
XLS_FORMAT = 'xls'
XML_FORMAT = 'xml'

EXT_FORMATS = {
    '.yml': YAML_FORMAT,
    '.yaml': YAML_FORMAT,
    '.json': JSON_FORMAT,
    '.xlsx': XLS_FORMAT,
    '.xls': XLS_FORMAT,
    '.xml': XML_FORMAT,
}

def _lookup_format(path):
    try:
        return EXT_FORMATS[os.path.splitext(path)[1]]
    except KeyError:
        valid_extensions = ', '.join(list(EXT_FORMATS.keys()))
        raise ValueError(f'No valid format found for file [ {path} ]\n'
                            f'Valid extensions: [{valid_extensions}]')

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

def open_yaml(path_in):
    with open(path_in) as ff:
        return yaml.safe_load(ff.read())


def form_to_xform(form_content, default_settings=None):
    export_kwargs = {}
    if default_settings:
        export_kwargs['default_settings'] = default_settings
    flat_json = form_content.export_to('xlsform', **export_kwargs)

    wbjson = xls2json.workbook_to_json(flat_json)
    survey = create_survey_element_from_dict(wbjson)
    if hasattr(survey, '_translations'):
        # tx_names is passed to the pyxform object to ensure the itext
        # translations show up in the correct order.
        # requires XLSForm/pyxform commit #68f0db99
        tx_names = []
        for tx in cc.txs.to_v1_strings():
            if tx is not None:
                tx_names.append(tx)
        for tx_name in tx_names:
            survey._translations[tx_name] = {}
    return survey._to_pretty_xml()


def print_form(form, validate=False, format=None, to_file=None):
    loaded_form = build_content(form, validate=validate)
    def printer(string_value):
        if to_file is None:
            print(string_value)
        else:
            with open(to_file, 'w') as ff:
                ff.write(string_value)

    if format == 'json':
        printer(json.dumps(loaded_form.export(), indent=2))
    elif format == 'yml':
        printer(form_to_yaml_string(loaded_form.export()))
    elif format == 'xml':
        default_settings = {'title': 'Form Title', 'identifier': 'generated'}
        xml = form_to_xform(loaded_form,
                            default_settings=default_settings)
        printer(xml)
    else:
        raise ValueError(f'Unknown format: {format}')

def run(path_in, path_out=None, validate=False, format=None):
    if format is None and path_out is None:
        # if no format or path is specified, then defualt output format is yml
        format = 'yml'
    elif format is None:
        format = _lookup_format(path_out)
    if not os.path.exists(path_in):
        raise ValueError('Path does not exist: ' + path_in)
    ext = _lookup_format(path_in)
    if ext == XLS_FORMAT:
        frm = open_xls(path_in)
    elif ext == YAML_FORMAT:
        frm = open_yaml(path_in)
    elif ext == JSON_FORMAT:
        frm = open_json(path_in)
    print_form(frm, validate=validate, format=format, to_file=path_out)

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
