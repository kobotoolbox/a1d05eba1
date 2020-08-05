'''
xlsform_choices:

if content.choices is a list, convert it to an object.

if it does not exist, add an empty object
'''

from .transformer import Transformer

class XlsformChoices(Transformer):
    '''
    converts an array of choices with "list_name" into a dictionary of lists
    keyed by list_name
    '''
    def rw(self, content):
        if 'choices' not in content:
            return content.copy_in(choices={})
        if isinstance(content['choices'], (list, tuple)):
            (content, choices_arr) = content.popout('choices')
            choices = {}
            for choice in choices_arr:
                (choice, list_name) = choice.popout('list_name')
                if list_name not in choices:
                    choices[list_name] = []
                choices[list_name].append(choice)
            return content.copy_in(choices=choices)
        return content
