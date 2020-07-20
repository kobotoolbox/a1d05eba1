'''
form_to_yaml_string returns an ordered YAML structure with sections and columns
organized to be consistent across the examples in this repository
'''

import oyaml
from collections import OrderedDict

def ordered_cols(item, preferred_col_order):
    row = OrderedDict()
    for col in preferred_col_order:
        value = item.pop(col, None)
        if value:
            row[col] = value
    for remaining in item.keys():
        row[remaining] = item.get(remaining)
    return row

def ordered_sheet(items, preferred_col_order):
    return [
        ordered_cols(item, preferred_col_order) for item in items
    ]

def form_to_yaml_string(form):
    order = OrderedDict()
    order['schema'] = []
    order['survey'] = [
        'type',
        'select_from',
        'name',
        'label',
    ]
    order['choices'] = [
        'value',
        'label',
    ]
    output = OrderedDict()
    for (section, col_orders) in order.items():
        value = form.pop(section, None)
        if not value:
            continue
        if section == 'choices':
            ordered_choices = OrderedDict()
            for cname, citems in value.items():
                ordered_choices[cname] = ordered_sheet(citems, col_orders)
            output[section] = ordered_choices
        else:
            if col_orders:
                output[section] = ordered_sheet(value, col_orders)
            else:
                output[section] = value
    for (section, contents) in form.items():
        output[section] = contents
    return oyaml.dump(output)
