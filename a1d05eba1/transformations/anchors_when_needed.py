'''
xlsform_add_anchors:

iterate through survey and choices to ensure all questions have a valid
"$anchor". These anchors are relied on throughout the code and must be unique
'''

from .transformer import Transformer, TransformerFW

# tells the main class to generate a random anchor
RAND_ANCHOR_KEY = '!RAND'

class AnchorsFromRandom(Transformer):
    def rw__each_row(self, row):
        if '$anchor' in row:
            return row
        return row.copy(**{'$anchor': RAND_ANCHOR_KEY})

    def rw__each_choice(self, cx, list_name):
        if '$anchor' in cx:
            return cx
        return cx.copy(**{'$anchor': RAND_ANCHOR_KEY})

class AnchorsFromNameOrRandom(Transformer):
    def rw__each_row(self, row):
        if '$anchor' in row:
            return row
        if 'name' in row:
            return row.copy(**{'$anchor': row.get('name')})
        return row.copy(**{'$anchor': RAND_ANCHOR_KEY})

    def rw__each_choice(self, cx, list_name):
        if '$anchor' in cx:
            return cx
        # if 'value' not in cx:
        if 'value' in cx:
            cx_value = cx['value']
            _list_name_value = f'{list_name}.{cx_value}'
            return cx.copy(**{'$anchor': _list_name_value})
        return cx.copy(**{'$anchor': RAND_ANCHOR_KEY})


class DumpExtraneousAnchorsFW(TransformerFW):
    def fw(self, content):
        choice_lists = {}
        for list_name, _choices in content['choices'].items():
            choices = tuple()
            for cx in _choices:
                if 'value' in cx:
                    ank = '{}.{}'.format(list_name, cx['value'])
                    if cx['$anchor'] == ank:
                        (cx, ank) = cx.popout('$anchor')
                choices = choices + (cx,)
            choice_lists[list_name] = choices
        return content.copy_in(choices=choice_lists)
