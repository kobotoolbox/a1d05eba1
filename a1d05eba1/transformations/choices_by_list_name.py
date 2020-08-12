'''
choices_by_list_name:

change columns that are essential for the rest of the transformer
functions to work. E.g. choices[n]['list name'] becomes list_name
'''

from collections import defaultdict

from .transformer import TransformerRW, TransformerFW
from ..utils.kfrozendict import kfrozendict


class ChoicesByListNameRW(TransformerRW):
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
        if 'choices' not in content:
            return content.copy(choices=kfrozendict())
        if isinstance(content['choices'], kfrozendict):
            return content

        _choices = content['choices']
        if isinstance(_choices, (list, tuple)):
            choice_lists = defaultdict(list)
            for _choice in _choices:
                choice = self._fix_choice(_choice)
                if 'list_name' not in choice:
                    continue
                (choice, list_name) = choice.popout('list_name')
                choice_lists[list_name].append(choice)
            return content.copy_in(choices=choice_lists)
        return content

class ChoicesToListFW(TransformerFW):
    def fw(self, content):
        choices_list = ()
        for (list_name, _choices) in content.get('choices', {}).items():
            for _cx in _choices:
                choices_list = choices_list + (_cx.copy(list_name=list_name),)
        return content.copy(choices=choices_list)
