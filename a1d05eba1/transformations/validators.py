'''
the idea is that these validators can be used in a chain of transformers
to ensure that the content matches what's needed.
'''

from .transformer import Transformer
from ..exceptions import StructureError


class ChoicesNotList(Transformer):
    def rw(self, content):
        if 'choices' in content:
            if isinstance(content['choices'], (list, tuple)):
                message = 'transformers out of order. ' \
                          'content.choices must be a dict'
                raise StructureError(message)

class SettingsNotList(Transformer):
    def rw(self, content):
        if 'settings' in content:
            if isinstance(content['settings'], (list, tuple)):
                message = 'transformers out of order.' \
                          'content.settings must be a dict'
                raise StructureError(message)

class HasTranlsations(Transformer):
    def rw(self, content):
        try:
            tx1_name = content['translations'][0]['name']
        except (KeyError, IndexError):
            message = 'content.translations must have at least one ' \
                      'translation specified'
            raise StructureError(message)
        except TypeError:
            message = 'content.translation[n] must be an object'
            raise StructureError(message)

def _each_choice(choices):
    if isinstance(choices, (list, tuple)):
        for choice in choices:
            yield choice
    else:
        for (cname, clist) in choices.items():
            for choice in clist:
                yield choice

class UniqueAnchors(Transformer):
    def rw(self, content):
        anchors = []
        def add_anchor(anchor):
            if anchor in anchors:
                message = 'anchor {} is not unique'.format(anchor)
                raise StructureError(message)
            anchors.append(anchor)
        try:
            for row in content['survey']:
                add_anchor(row['$anchor'])
            for choice in _each_choice(content['choices']):
                add_anchor(choice['$anchor'])
        except KeyError:
            raise StructureError('Missing unique $anchor')

unique_anchors = UniqueAnchors()
choices_not_list = ChoicesNotList()
settings_not_list = SettingsNotList()
has_translations = HasTranlsations()
