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

from ..utils.yparse import yload_file

from ..schema_properties import (
    TRANSLATABLE_SURVEY_COLS,
    TRANSLATABLE_CHOICES_COLS,
)

from .transformer import Transformer

NULL_TRANSLATION = 'NULL_TRANSLATION'
TRANSLATABLE_V1_COLS = yload_file('renames/from1/translatable-columns')

TRANSLATABLE_COLS = set(
    TRANSLATABLE_V1_COLS + \
    TRANSLATABLE_SURVEY_COLS + \
    TRANSLATABLE_CHOICES_COLS
)


def expand_it(row, updates, translated, translations):
    for col in translated:
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


def inspect_content_translations(content):
    ctx = SimpleNamespace(NULL_TRANSLATION=NULL_TRANSLATION)
    translatable_col_match = []
    for txable in TRANSLATABLE_COLS:
        translatable_col_match.append(['^%s::?([^:]*)$' % txable, txable])

    ctx.tx_colnames = {}
    ctx.translations = []
    ctx.translated = set()

    def gather_txs(row):
        for col in TRANSLATABLE_COLS:
            if col in row:
                if NULL_TRANSLATION not in ctx.translations:
                    ctx.translations.append(NULL_TRANSLATION)
                _index = ctx.translations.index(NULL_TRANSLATION)
                ctx.tx_colnames[col] = [col, NULL_TRANSLATION, _index]
                # if col not in ctx.translated:
                ctx.translated = ctx.translated.union([col])
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

    for sheet in ['survey', 'choices']:
        for row in content.get(sheet, []):
            gather_txs(row)
        # ugly fix for temporary problem?
        # formpack has surveys with labels looking like ["hi"]
        # on untranslated surveys. Does this exist elsewhere? TBD
        ctx.needs_mutation = len(ctx.translations) != 1 or \
                             ctx.translations[0] != NULL_TRANSLATION
    ctx.tx_count = len(ctx.translations)
    return ctx


def mutate_content(content, context, strict=True):
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

    for sheet_name in ['survey', 'choices']:
        sheet = tuple()
        for row in content.get(sheet_name, []):
            sheet = sheet + (mutate_row(row),)
        content = content.copy(**{sheet_name: sheet})

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


class XlsformTranslationsStrict(Transformer):
    strict = True

    def fw(self, content):
        assert content['schema'].startswith('1')
        (content, translations) = content.popout('translations')
        (content, translated) = content.popout('translated')
        (content, survey_in) = content.popout('survey')
        content_updates = {'survey': []}
        for row in survey_in:
            row_updates = {}
            if 'select_from_list_name' in row:
                (row, list_name) = row.popout('select_from_list_name')
                row_updates['type'] = ' '.join([row['type'], list_name])
            row = expand_it(row,
                            updates=row_updates,
                            translated=translated,
                            translations=translations,
                            )
            content_updates['survey'].append(row.copy(**row_updates))

        (content, choices) = content.popout('choices')
        content_updates['choices'] = []
        for cx in choices:
            choice_updates = {}
            cx = expand_it(cx,
                           updates=choice_updates,
                           translated=translated,
                           translations=translations,
                           )
            content_updates['choices'].append(cx.copy(**choice_updates))
        return content.copy_in(**content_updates)


    def rw(self, content):
        context = inspect_content_translations(content)
        if not context.needs_mutation:
            if 'translations' not in content:
                return content.copy(translations=context.translations)
            return content
        return mutate_content(content, context, self.strict)

class XlsformTranslations(XlsformTranslationsStrict):
    strict = False

TRANSFORMER = XlsformTranslationsStrict()
NOT_STRICT = XlsformTranslations()
