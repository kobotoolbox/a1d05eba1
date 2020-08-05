'''
xlsform_add_anchors:

iterate through survey and choices to ensure all questions have a valid
"$anchor". These anchors are relied on throughout the code and must be unique
'''

from .transformer import Transformer

# tells the main class to generate a random anchor
RAND_ANCHOR_KEY = '!RAND'

class EnsureAnchorsWhenNeeded(Transformer):
    def rw__each_row(self, row):
        if '$anchor' not in row and 'name' not in row:
            return row.copy(**{'$anchor': RAND_ANCHOR_KEY})

    def rw__each_choice(self, cx, list_name):
        _no_anchor = '$anchor' not in cx
        if _no_anchor and ('value' in cx and 'list_name' in cx):
            return cx.copy(**{
                '$anchor': '{}.{}'.format(list_name, cx['value']),
            })
        elif _no_anchor:
            return cx.copy(**{'$anchor': RAND_ANCHOR_KEY})

class DumpExtraneousAnchors(Transformer):
    def fw(self, content):
        _choice_lists = {}
        for list_name, choices in content['choices'].items():
            _choices = tuple()
            for cx in choices:
                if 'value' in cx:
                    ank = '{}.{}'.format(list_name, cx['value'])
                    if cx['$anchor'] == ank:
                        (cx, ank) = cx.popout('$anchor')
                _choices = _choices + (cx,)
            _choice_lists[list_name] = _choices
        return content.copy_in(choices=_choice_lists)
