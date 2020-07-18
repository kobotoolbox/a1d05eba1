'''
remove_empty_rows:

requires: content.schema == '1'

remove rows which have no meaning.
in the "survey" sheet, that means any row without a "type" value.
in the "choices" sheet, this is any row with a "list_name" value.


rw:
---------------------------
    * Iterates through "survey" and "choices" sheets to remove empty or invalid rows
    (i.e. rows with no "type" column)

    * Preserves rows which may be ruled invalid later on (e.g. unknown type)
'''

from .transformer import Transformer


def remove_empties_from_list(surv_in, required_key='type'):
    surv_out = tuple()
    for row in surv_in:
        if len(row) == 0:
            continue
        val = row.get(required_key, '')
        if val != '':
            surv_out = surv_out + (row,)
    return surv_out


class RemoveEmpties(Transformer):
    # ASSERT_CONTENT_SCHEMA = '1'

    def rw(self, content):
        assert content['schema'] == '1'
        choices = content.get('choices', [])
        updates = {
            'survey': remove_empties_from_list(content['survey']),
            'choices': remove_empties_from_list(choices, required_key='list_name'),
        }
        return content.copy(**updates)

TRANSFORMER = RemoveEmpties()
