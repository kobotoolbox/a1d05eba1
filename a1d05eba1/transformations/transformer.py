from ..utils.kfrozendict import kfrozendict
import sys


def _pprint(cc, indent=4):
    import pprint
    ss = pprint.pformat(cc, indent=1, width=120)
    if indent > 0:
        spaces = ' ' * indent
        ss = '\n'.join([(spaces + line) for line in ss.split('\n')])
    print(ss)


class Transformer:
    name = None

    def __init__(self):
        if self.name is None:
            self.name = self.__class__.__name__

    def fw(self, content):
        updates = {}
        if hasattr(self, 'fw__each_row'):
            survey = ()
            for row in content.get('survey', []):
                survey = survey + (
                    (self.fw__each_row(row) or row),
                )
            updates['survey'] = survey
        if 'choices' in content and hasattr(self, 'fw__each_choice'):
            is_list = isinstance(content['choices'], (list, tuple))
            if is_list:
                updates['choices'] = self._fw_iterchoices(content['choices'])
            else:
                choice_updates = {}
                for (cname, clist) in content['choices'].items():
                    choice_updates[cname] = self._fw_iterchoices(clist)
                updates['choices'] = kfrozendict.freeze(choice_updates)
        if len(updates) > 0:
            return content.copy(**updates)

    def _fw_iterchoices(self, cxs):
        choices = ()
        for choice in cxs:
            choices = choices + (self.fw__each_choice(choice),)
        return choices

    def rw(self, content):
        updates = {}
        if hasattr(self, 'rw__each_row'):
            survey = ()
            for row in content.get('survey', []):
                survey = survey + (
                    (self.rw__each_row(row) or row),
                )
            updates['survey'] = survey
        if 'choices' in content and hasattr(self, 'rw__each_choice'):
            is_list = isinstance(content['choices'], (list, tuple))
            if is_list:
                updates['choices'] = self._rw_iterchoices(content['choices'])
            else:
                choice_updates = {}
                for (cname, clist) in content['choices'].items():
                    choice_updates[cname] = self._rw_iterchoices(clist)
                updates['choices'] = kfrozendict.freeze(choice_updates)
        return content.copy(**updates)

    def _rw_iterchoices(self, cxs):
        choices = ()
        for choice in cxs:
            choices = choices + (self.rw__each_choice(choice) or choice,)
        return choices


def unwrap(tt):
    return tt if not hasattr(tt, 'TRANSFORMER') else tt.TRANSFORMER

class TransformerList:
    def __init__(self, transformers=(), name='', debug=False):
        self.name = name
        self._debug = debug
        self.transformers = []
        for tfn in transformers:
            tfn = unwrap(tfn)
            assert isinstance(tfn, (Transformer, TransformerList))
            self.transformers.append(tfn)

    def ensure(self, transformer):
        transformer = unwrap(transformer)
        assert isinstance(transformer, Transformer)
        if transformer not in self.transformers_iter():
            self.transformers.append(transformer)

    def transformers_iter(self):
        for transformer in self.transformers:
            if isinstance(transformer, TransformerList):
                for sub_transformer in transformer.transformers_iter():
                    yield sub_transformer
            else:
                yield transformer

    def _apply_transformers(self, content, is_rw, stack=()):
        if self._debug:
            print('<'+self.name+'>')
            if self.name == 'root':
                print('  <input>')
                _pprint(content.uf)
                print('  </input>\n')


        transformer_list = self.transformers[:]

        if not is_rw:
            transformer_list.reverse()

        stack = stack + (self.name,)

        for transformer in transformer_list:
            if isinstance(transformer, TransformerList):
                if is_rw:
                    _content = transformer.rw(content, stack=stack)
                else:
                    _content = transformer.fw(content, stack=stack)
            else:
                if is_rw:
                    _content = transformer.rw(content)
                else:
                    _content = transformer.fw(content)

            if self._debug and _content:
                print('\n [*] ' + ':'.join(stack) + '::' + transformer.name)
                print(' ------------')
                _pprint(_content.uf)
            elif self._debug:
                print('\n [ ] ' + ':'.join(stack) + '::' + transformer.name)

            if _content:
                content = _content
        if self._debug:
            if self.name == 'root':
                print('\n  <output>')
                _pprint(content.uf)
                print('  </output>')

            print('</'+self.name+'>')
        return content

    def rw(self, content, stack=()):
        return self._apply_transformers(content, True, stack=stack)

    def fw(self, content, stack=()):
        return self._apply_transformers(content, False, stack=stack)
