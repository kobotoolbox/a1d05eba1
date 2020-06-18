'''
this "transformer" will convert arrays
    survey[], choices.xxxabc[], choices.xxxdef[]
into objects keyed with one '$start', and '$next' values pointing to '$anchor'

    Example:
    [
        {'$anchor': 'aaa'},
        {'$anchor': 'bbb'},
        {'$anchor': 'ccc'},
    ]

    {
        '$start': 'aaa',
        'aaa': {'$next': 'bbb'},
        'bbb': {'$next': 'ccc'},
        'ccc': {},
    }

'''

ANCHOR_KEY = '$anchor'


# forwards
def fw(content):
    (content, survey) = content.popout('survey')
    (content, choices) = content.popout('choices')
    replacements = {}
    def pull_array_to_defs(_survey):
        if len(_survey) is 0:
            return {'$start': None}
        anchor1 = _survey[0][ANCHOR_KEY]
        defs = {'$start': anchor1}
        _next = False
        for row in _survey[::-1]:
            (row, anchor) = row.popout(ANCHOR_KEY)
            if _next != False:
                row = row.copy(**{'$next': _next})
            _next = anchor
            defs[anchor] = row
        return defs
    replacements['survey'] = pull_array_to_defs(survey)

    replacements['choices'] = {}
    for (choice_list_name, _choices) in choices.items():
        replacements['choices'][choice_list_name] = pull_array_to_defs(_choices)

    return content.copy_in(**replacements)

# backwards
def rw(content):
    (content, survey) = content.popout('survey')
    (content, choices) = content.popout('choices')

    def restore_it(hsh):
        out = []
        next_key = hsh['$start']
        while next_key:
            (next_val, next_key) = hsh[next_key].copy(**{
                ANCHOR_KEY: next_key,
            }).popout('$next')
            out.append(next_val)
        return out

    copy_that = {}
    copy_that['survey'] = restore_it(survey)

    if choices:
        copy_choices = {}
        for choice_list_name, cxs in choices.items():
            copy_choices[choice_list_name] = restore_it(cxs)
        copy_that['choices'] = copy_choices

    return content.copy_in(**copy_that)
