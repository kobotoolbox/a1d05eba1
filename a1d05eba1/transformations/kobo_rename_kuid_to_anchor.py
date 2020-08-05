'''
kobo_rename_kuid_to_anchor:

iterate through survey and choices to ensure all questions have a valid
"$anchor". These anchors are relied on throughout the code and must be unique
'''

from .transformer import Transformer

class RenameKuidToAnchor(Transformer):
    def fw__each_row(self, row):
        if '$anchor' in row:
            return row.renamed('$anchor', '$kuid')

    def fw__each_choice(self, choice):
        if '$anchor' in choice:
            return choice.renamed('$anchor', '$kuid')

    def rw__each_row(self, row):
        if '$kuid' in row:
            return row.renamed('$kuid', '$anchor')

    def rw__each_choice(self, choice, list_name):
        if '$kuid' in choice:
            return choice.renamed('$kuid', '$anchor')

TRANSFORMER = RenameKuidToAnchor()
