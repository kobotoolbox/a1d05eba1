from ..utils.kfrozendict import kfrozendict
from ..exceptions import DirectionalTransformerError

class Transformer:
    '''
    The following functions are intended to be overridden in these "Transformer"
    classes:

    - rw
    - rw__{n}               # where {n} is the schema number
    - rw__each_row
    - rw__each_choice
    - rw__{n}__each_row
    - rw__{n}__each_choice

    - fw
    - fw__{n}
    - fw__each_row
    - fw__each_choice
    - fw__{n}__each_row
    - fw__{n}__each_choice
    '''

    name = None
    assert_schema = None

    def __init__(self):
        if self.name is None:
            self.name = self.__class__.__name__

    def rwfw(self, content, direction, stack, debug):
        # has the same interface as transformer_list.rwfw
        if direction == 'rw':
            return self.rw(content)
        else:
            return self.fw(content)

    def rw(self, content):
        return self._first_defined_subclassed_function((
            'rw__{schema}'.format(schema=content['schema']),
            '_rw',
        ))(content)

    def _rw(self, content):
        # only executed if "self.rw()" is not defined
        return self.transform_content(content, direction='rw')

    def fw(self, content):
        return self._first_defined_subclassed_function((
            'fw__{schema}'.format(schema=content['schema']),
            '_fw',
        ))(content)

    def _fw(self, content):
        return self.transform_content(content, direction='fw')

    def transform_content(self, content, direction, **kwargs):
        schema = content['schema']

        updates = {}

        # try each subblassed iterable function
        (each_row_fn, each_choice_fn) = (
            self._first_defined_subclassed_function((
                '%s__%s__each_%s' % (direction, schema, item),
                '%s__each_%s' % (direction, item),
            )) for item in ['row', 'choice']
        )

        settings_fn = self._first_defined_subclassed_function((
            f'{direction}__{schema}__settings',
            f'{direction}__settings',
        ))
        if settings_fn:
            updates['settings'] = settings_fn(content['settings'])

        if each_row_fn:
            survey = ()
            for row in content['survey']:
                survey = survey + (
                    each_row_fn(row) or row,
                )
            updates['survey'] = survey

        if each_choice_fn and 'choices' in content:
            updates['choices'] = choice_updates = {}
            if not isinstance(content['choices'], kfrozendict):
                raise ValueError('content.choices cannot be a list. '
                                 'See: transformers.ChoicesByListNameRW')
            for (list_name, clist) in content['choices'].items():
                choices = ()
                for choice in clist:
                    choices = choices + (
                        each_choice_fn(choice, list_name=list_name) or choice,
                    )
                choice_updates[list_name] = choices

        return content.copy_in(**updates)

    def _first_defined_subclassed_function(self, each_fns):
        for each_fn in each_fns:
            fn = getattr(self, each_fn, None)
            if fn:
                return fn
        return fn

class TransformerRW(Transformer):
    def fw(self, *args, **kwargs):
        raise DirectionalTransformerError(a1='rw()', a2='FW', name=self.name)


class TransformerFW(Transformer):
    def rw(self, *args, **kwargs):
        raise DirectionalTransformerError(a1='fw()', a2='RW', name=self.name)
