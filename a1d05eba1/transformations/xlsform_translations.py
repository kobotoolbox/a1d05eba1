'''
xlsform_translations:

parse the columns like "label::English" and construct a structure with
all the "label" values in one array

input:

    survey[n]
        {'type': 'text', 'label::english': 'blah'}


output:

    survey[n]
        {'type': 'text', 'label': ['blah']}
    translations
        ['english']

'''

import re
from types import SimpleNamespace

from ..utils.kfrozendict import kfrozendict
from ..utils.yparse import yload_file

from ..schema_properties import (
    TRANSLATABLE_SURVEY_COLS,
    TRANSLATABLE_CHOICES_COLS,
)

from .transformer import Transformer, TransformerRW
from .transformer_list import TransformerList

NULL_TRANSLATION = 'NULL_TRANSLATION'
TRANSLATABLE_V1_COLS = yload_file('renames/from1/translatable-columns')

TRANSLATABLE_COLS = set(
    TRANSLATABLE_V1_COLS + \
    TRANSLATABLE_SURVEY_COLS + \
    TRANSLATABLE_CHOICES_COLS
)

RENAMES_FROM_V1 = yload_file('renames/from1/column')

def expand_it(row, updates, translations):
    for col in TRANSLATABLE_COLS:
        (row, vals) = row.popout(col)
        if vals:
            for (tx, val) in zip(translations, vals):
                if val is None:
                    continue
                if tx in [None, '']:
                    newcolname = col
                else:
                    newcolname = '::'.join([col, tx])
                updates[newcolname] = val
    return row


def _translatable_cols_iter():
    for txable in TRANSLATABLE_COLS:
        yield txable, txable
        if txable not in RENAMES_FROM_V1:
            continue
        for alias in RENAMES_FROM_V1[txable]:
            yield alias, txable


def rw_inspect_content_translations(content):
    ctx = SimpleNamespace(NULL_TRANSLATION=NULL_TRANSLATION)
    translatable_col_match = []

    for alias, colname in _translatable_cols_iter():
        translatable_col_match.append(['^%s::?([^:]*)$' % alias, colname])

    ctx.tx_colnames = {}
    ctx.translations = []
    ctx.translated = set()

    def gather_txs(row):
        for alias, colname in _translatable_cols_iter():
            col = alias
            if alias in row:
                if NULL_TRANSLATION not in ctx.translations:
                    ctx.translations.append(NULL_TRANSLATION)
                _index = ctx.translations.index(NULL_TRANSLATION)
                ctx.tx_colnames[alias] = [colname, NULL_TRANSLATION, _index]
                ctx.translated = ctx.translated.union([colname])
        for colname in row.keys():
            for [rxp, intended_col_name] in translatable_col_match:
                mtch = re.match(rxp, colname)
                if mtch:
                    [lang] = mtch.groups()
                    lang =  lang.strip()
                    if lang == '':
                        lang = NULL_TRANSLATION
                    if lang not in ctx.translations:
                        ctx.translations.append(lang)
                    _index = ctx.translations.index(lang)
                    ctx.tx_colnames[colname] = [intended_col_name, lang, _index]
                    ctx.translated = ctx.translated.union([intended_col_name])

    for row in content.get('survey', []):
        gather_txs(row)
    for (list_name, choices) in content.get('choices', {}).items():
        for choice in choices:
            gather_txs(choice)
    # ugly fix for temporary problem?
    # formpack has surveys with labels looking like ["hi"]
    # on untranslated surveys. Does this exist elsewhere? TBD
    ctx.needs_mutation = len(ctx.translations) != 1 or \
                         ctx.translations[0] != NULL_TRANSLATION
    ctx.tx_count = len(ctx.translations)
    return ctx


def rw_mutate_content(content, context, strict=True):
    def mutate_row(row):
        label = row.get('label')
        if strict and isinstance(label, (list, tuple)):
            raise ValueError('must be not a list')
        overrides = {}
        dests = {}
        for key in row.keys():
            if key in context.tx_colnames:
                (row, val) = row.popout(key)
                (destination, lang, index) = context.tx_colnames[key]
                if destination not in dests:
                    dests[destination] = [None] * context.tx_count
                dests[destination][index] = val
        row = row.copy(**dests)
        return row

    survey_sheet = tuple()
    for row in content.get('survey', []):
        survey_sheet = survey_sheet + (
            mutate_row(row),
        )
    content = content.copy(survey=survey_sheet)

    if 'choices' in content and len(content['choices']) > 0:
        choice_lists = {}
        for (list_name, choices) in content['choices'].items():
            choice_lists_list_name = ()
            for choice in choices:
                choice_lists_list_name = choice_lists_list_name + (
                    mutate_row(choice),
                )
            choice_lists[list_name] = choice_lists_list_name
        content = content.copy(choices=kfrozendict(choice_lists))
    else:
        content = content.copy(choices=kfrozendict())

    translations = []
    for tx in context.translations:
        translations.append(
            NULL_TRANSLATION
            if tx == context.NULL_TRANSLATION
            else tx
        )
    translated = sorted(context.translated)
    changes = {
      'translations': translations,
      'translated': translated,
      'schema': '1',
    }
    return content.copy(**changes)


class XlsformTranslations(Transformer):
    strict = False

    def fw__1(self, content):
        (content, translations) = content.popout('translations')
        (content, survey_in) = content.popout('survey')
        content_updates = {'survey': []}
        for row in survey_in:
            row_updates = {}
            if 'select_from_list_name' in row:
                (row, list_name) = row.popout('select_from_list_name')
                row_updates['type'] = ' '.join([row['type'], list_name])
            row = expand_it(row,
                            updates=row_updates,
                            # translated=translated,
                            translations=translations,
                            )
            content_updates['survey'].append(row.copy(**row_updates))

        (content, choice_lists) = content.popout('choices')
        _choice_updates = {}
        for list_name, choices in choice_lists.items():
            _cur_list = ()
            for choice in choices:
                cx_updates = {}
                cx = expand_it(choice,
                               updates=cx_updates,
                               translations=translations,
                               )
                _cur_list = _cur_list + (
                    cx.copy(**cx_updates),
                )
            _choice_updates[list_name] = _cur_list
        content_updates['choices'] = _choice_updates
        return content.copy_in(**content_updates)

    def rw__1(self, content):
        context = rw_inspect_content_translations(content)
        if not context.needs_mutation:
            if 'translations' not in content:
                return content.copy(translations=context.translations)
            return content
        return rw_mutate_content(content, context, self.strict)

class XlsformTranslationsStrict(XlsformTranslations):
    strict = True

class EnsureTranslationListRW(TransformerRW):
    def rw(self, content):
        if 'translations' not in content:
            return content.copy_in(translations=[None])
        return content
