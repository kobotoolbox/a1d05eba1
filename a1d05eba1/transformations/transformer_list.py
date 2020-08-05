
import json
from pprint import pformat

from ..utils.kfrozendict import kfrozendict, deepfreeze


def indented_pprint(cc, indent=4):
    ss = cc
    if not isinstance(cc, str):
        ss = pformat(cc, indent=1, width=120)
    if indent > 0:
        spaces = ' ' * indent
        ss = '\n'.join([(spaces + line) for line in ss.split('\n')])
    print(ss)


class TransformerList:
    _debug = False
    transformers = ()

    def __init__(self, transformers=(), name='', debug=False, root=False):
        self.name = self.__class__.__name__
        if root:
            self.name = 'root'
        self._debug = debug
        for tfn in transformers:
            assert self.is_transformer(tfn)
            self.transformers = self.transformers + (tfn,)

    def is_transformer(self, tfn):
        return hasattr(tfn, 'rw') and hasattr(tfn, 'fw')

    def ensure(self, transformer):
        assert self.is_transformer(transformer)
        if transformer not in self.transformers_iter():
            self.transformers = self.transformers + (transformer,)

    def transformers_iter(self):
        for transformer in self.transformers:
            if isinstance(transformer, TransformerList):
                for sub_transformer in transformer.transformers_iter():
                    yield sub_transformer
            else:
                yield transformer

    def _apply_transformers(self, content, is_rw, stack=(), debug=None):
        if debug is not None:
            self._debug = debug
        if self._debug:
            oindent = '    ' * len(stack)
            print('\n' + oindent +'<'+self.name+' direction="' + ('rw' if is_rw else 'fw') + '">')
            if self.name == 'root':
                print('  <input>')
                indented_pprint(content.uf)
                print('  </input>\n')


        transformer_list = list(self.transformers[:])

        if not is_rw:
            transformer_list.reverse()

        stack = stack + (self.name,)

        for transformer in transformer_list:
            transformer = transformer()

            if isinstance(transformer, TransformerList):
                if is_rw:
                    _content = transformer.rw(content, stack=stack, debug=self._debug)
                else:
                    _content = transformer.fw(content, stack=stack, debug=self._debug)
            else:
                if is_rw:
                    _content = transformer.rw(content)
                else:
                    _content = transformer.fw(content)
                if 'choices' in _content:
                    assert isinstance(_content['choices'], (dict, kfrozendict))
                if 'settings' in _content:
                    assert isinstance(_content['settings'], (dict, kfrozendict))

            if self._debug:
                has_change = deepfreeze(content) != deepfreeze(_content)
                _name = ':'.join(stack) + '::' + transformer.name
                _name_att = 'name="%s"' % _name

                indent = '    ' * len(stack)
                indent_n = len(stack)
                _topen = '<transformer ' + _name_att
                if has_change:
                    _topen += ' changed="+">'
                else:
                    _topen += ' nochange>'
                indented_pprint(_topen, indent_n)
                if has_change:
                    indented_pprint(_topen, indent_n)
                    indented_pprint(_content.uf, indent_n)
                    indented_pprint('</transformer>', indent_n)

            if _content:
                content = _content

        if self._debug:
            if self.name == 'root':
                print('\n' + indent + '<output>')
                indented_pprint(content.uf, indent_n)
                print(indent + '</output>')
            print(oindent + '</'+self.name+'>')

        return content

    def rw(self, content, **kwargs):
        if 'choices' in content:
            assert isinstance(content['choices'], (kfrozendict, dict))
        if 'settings' in content:
            assert isinstance(content['settings'], (kfrozendict, dict))
        return self._apply_transformers(content, is_rw=True, **kwargs)

    def fw(self, content, **kwargs):
        return self._apply_transformers(content, is_rw=False, **kwargs)
