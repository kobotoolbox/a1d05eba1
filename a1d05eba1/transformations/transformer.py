class Transformer:
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


class TransformerList:
    def __init__(self, transformers=()):
        self.transformers = []
        self.transformers_rw = []
        self.transformers_fw = []
        for tfn in transformers:
            self.add(tfn)

    def add(self, transformer):
        # allow a module with a TRANSFORMER attribute to be added
        if hasattr(transformer, 'TRANSFORMER'):
            transformer = transformer.TRANSFORMER
        self.transformers.append(transformer)
        if hasattr(transformer, 'rw'):
            self.transformers_rw.append(transformer.rw)
        if hasattr(transformer, 'fw'):
            self.transformers_fw.insert(0, transformer.fw)

    def ensure(self, transformer):
        if transformer not in self.transformers:
            self.add(transformer)

    def _apply_transformers(self, content, transformer_list, is_rw):
        for t_fn in transformer_list:
            _content = t_fn(content)
            if _content:
                content = _content
        return content

    def rw(self, content):
        return self._apply_transformers(content, self.transformers_rw, True)

    def fw(self, content):
        return self._apply_transformers(content, self.transformers_fw, False)

'''
class TxDebug(Transformer):
    def __init__(self, **kwargs):
        self.if_row = kwargs.pop('if_row', None)
        self.info = kwargs.pop('info', None)
        self.if_row_then = kwargs.pop('then', 'pause')
        self.print_settings = kwargs.pop('print_settings', False)
    def rw(self, content):
        if self.print_settings:
            if self.info:
                print(self.info)
            setts = content.get('settings', False)
            pprint(kfrozendict.unfreeze(setts))
        if self.if_row:
            for row in content['survey']:
                if self.if_row(row):
                    if self.info:
                        print(self.info)
                    if self.if_row_then == 'pause':
                        import pdb; pdb.set_trace()
                    elif self.if_row_then == 'print':
                        pprint(kfrozendict.unfreeze(row))
        return content
'''
