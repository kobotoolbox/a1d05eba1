'''
xlsform_initial_renames:

change columns that are essential for the rest of the transformer
functions to work. E.g. choices[n]['list name'] becomes list_name
'''

from .transformer import Transformer

class InitialRenames(Transformer):
    def rw__each_choice(self, choice):
        if 'list name' in choice:
            choice = choice.renamed('list name', 'list_name')
        return choice

TRANSFORMER = InitialRenames()
