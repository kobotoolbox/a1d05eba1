'''
renames a kobo-specific row identifier: "$kuid" when the content
is loaded.
'''

from ..utils.anchor_generator import anchor_generator


def fw(content):
    survey = ()
    for row in content.get('survey', []):
        if '$anchor' in row:
            (row, anchor) = row.popout('$anchor')
            row = row.copy(**{'$kuid': anchor})
        survey = survey + (row,)
    return content.copy(survey=survey)

def rw(content):
    survey = ()
    for row in content.get('survey', []):
        if '$kuid' in row:
            (row, kuid) = row.popout('$kuid')
            row = row.copy(**{'$anchor': kuid})
        survey = survey + (row,)
    return content.copy(survey=survey)
