import re
from collections import defaultdict
from types import SimpleNamespace

from ..utils.yparse import yload_file

NULL_TRANSLATION = 'NULL_TRANSLATION'


TRANSLATABLE_COLS = yload_file('renames/from1/translatable-columns')


def expand_it(row, updates, translated, translations):
    for col in translated:
        (row, vals) = row.popout(col)
        if vals:
            for (tx, val) in zip(translations, vals):
                if tx in [None, '']:
                    newcolname = col
                else:
                    newcolname = '::'.join([col, tx])
                updates[newcolname] = val
    return row

def fw(content):
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
                ctx.tx_colnames[col] = [col, NULL_TRANSLATION, 0]
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
    ctx.tx_count = len(ctx.translations)
    return ctx

def mutate_content(content, context):
    def mutate_row(row):
        overrides = {}
        dests = {}
        for key in row.keys():
            if key in context.tx_colnames:
                (row, val) = row.popout(key)
                [destination, lang, index] = context.tx_colnames[key]
                if destination not in dests:
                    dests[destination] = [None] * context.tx_count
                dests[destination][index] = val
        row = row.copy(**dests)
        return row

    for sheet_name in ['survey', 'choices']:
        sheet = tuple()
        for row in content.get(sheet_name, []):
            sheet = (*sheet, mutate_row(row),)
        content = content.copy(**{sheet_name: sheet})

    translations = []
    for tx in context.translations:
        translations.append(
            None
            if tx == context.NULL_TRANSLATION
            else tx
        )
    translated = sorted(context.translated)
    changes = {
      'translations': translations,
      'translated': translated,
      'schema': '1',
    }
    settings = content.get('settings', {})
    if isinstance(settings, (list, tuple)):
        if len(settings) > 0:
            settings = settings[0]
        else:
            settings = {}
    changes['settings'] = settings
    return content.copy(**changes)


def rw(content):
    context = inspect_content_translations(content)
    return mutate_content(content, context)
