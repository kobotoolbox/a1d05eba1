'''
choices_by_list_name:

change columns that are essential for the rest of the transformer
functions to work. E.g. choices[n]['list name'] becomes list_name
'''

from .transformer import Transformer
from ..utils.kfrozendict import kfrozendict

class ChoicesByListName(Transformer):
    '''
    moves a list of choices to a dict of choices organized by list_name
    '''
    def _fix_choice(self, choice):
        if 'list name' in choice:
            choice = choice.renamed('list name', 'list_name')
        if 'name' in choice:
            choice = choice.renamed('name', 'value')
        return choice

    def rw(self, content):
        if 'choices' not in content or \
                isinstance(content['choices'], kfrozendict):
            return content
        _choices = content['choices']
        if isinstance(_choices, (list, tuple)):
            choice_lists = {}
            # choices = ()
            for _choice in _choices:
                choice = self._fix_choice(_choice)
                if 'list_name' not in choice:
                    continue
                (choice, list_name) = choice.popout('list_name')
                if list_name not in choice_lists:
                    choice_lists[list_name] = []
                choices = choice_lists[list_name]
                choices.append(choice)
            return content.copy_in(choices=choice_lists)
        return content
