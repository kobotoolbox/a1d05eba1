from .transformer import TransformerFW

from ..utils.kfrozendict import kfrozendict


class SettingsChoicesToListFW(TransformerFW):
    def fw__1(self, content):
        assert isinstance(content['settings'], kfrozendict)
        assert isinstance(content['choices'], kfrozendict)
        choices = ()
        for (list_name, _choices) in content['choices'].items():
            for choice in _choices:
                choices = choices + (choice.copy(list_name=list_name),)
        return content.copy(
            settings=(content['settings'],),
            choices=choices,
        )
