import json
from pprint import pformat

from ..utils.kfrozendict import kfrozendict, deepfreeze
from ..exceptions import DirectionalTransformerError


def indented_pprint(cc, indent=4):
    ss = cc
    if not isinstance(cc, str):
        ss = pformat(cc, indent=1, width=120)
    if indent > 0:
        spaces = ' ' * indent
        ss = '\n'.join([(spaces + line) for line in ss.split('\n')])
    print(ss)


class TransformerList:
    debug = False
    transformers = ()

    def __init__(self, transformers=(), name=None, debug=False):
        self.name = name or self.__class__.__name__
        self.debug = debug
        for tfn in transformers:
            assert self.is_transformer(tfn)
            self.transformers = self.transformers + (tfn,)

    def is_transformer(self, tfn):
        return hasattr(tfn, 'rw') and hasattr(tfn, 'fw')

    def _apply_transformers(self, content, direction, stack=(), debug=None):
        if debug is not None:
            self.debug = debug
        if self.debug:
            oindent = '    ' * len(stack)
            print(f'\n{oindent}<{self.name} direction="{direction}">')
            if self.name == 'root':
                print('  <input>')
                indented_pprint(content.uf)
                print('  </input>\n')

        transformer_list = list(self.transformers[:])

        stack = stack + (self.name,)

        for transformer in transformer_list:
            transformer = transformer()
            transformer_args = {'stack': stack, 'debug': self.debug}
            transformer_args['direction'] = direction

            _content = transformer.rwfw(content, **transformer_args)

            if self.debug:
                has_change = deepfreeze(content) != deepfreeze(_content)
                _name = ':'.join(stack) + '::' + transformer.name
                _name_att = 'name="%s"' % _name

                indent = '    ' * len(stack)
                indent_n = len(stack)
                _topen = '<transformer ' + _name_att
                if not has_change:
                    indented_pprint(f'{_topen} nochange />', indent_n)
                else:
                    indented_pprint(f'{_topen}>', indent_n)
                    indented_pprint(_content.uf, indent_n)
                    indented_pprint('</transformer>', indent_n)

            if _content:
                content = _content

        if self.debug:
            if self.name == 'root':
                print('\n' + indent + '<output>')
                indented_pprint(content.uf, indent_n)
                print(indent + '</output>')
            print(oindent + '</'+self.name+'>')

        return content

    def rwfw(self, content, direction, **kwargs):
        if direction == 'rw':
            return self.rw(content, **kwargs)
        else:
            return self.fw(content, **kwargs)

    def rw(self, content, **kwargs):
        return self._apply_transformers(content, direction='rw', **kwargs)
