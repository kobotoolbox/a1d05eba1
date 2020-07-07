'''
Requires: content.schema == '1'

Reverse function, aka "rw":
---------------------------
* Iterates through "survey" and "choices" sheets to remove empty or invalid rows
(i.e. rows with no "type" column)

* Preserves rows which may be ruled invalid later on (e.g. unknown type)

Forward function run on export
------------------------------

* forward function (run on "export") has no effect

'''

ASSERT_CONTENT_SCHEMA = '1'


def fw(content):
    pass

def remove_empties_from_list(surv_in, required_key='type'):
    surv_out = tuple()
    for row in surv_in:
        if len(row) == 0:
            continue
        val = row.get(required_key, '')
        if val != '':
            surv_out = surv_out + (row,)
    return surv_out


def rw(content):
    assert content['schema'] == '1'
    updates = {
        'survey': remove_empties_from_list(content['survey']),
        'choices': remove_empties_from_list(content['choices'], required_key='list_name'),
    }
    return content.copy(**updates)
