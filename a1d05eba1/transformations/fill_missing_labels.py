'''
fill_missing_labels

Prevents a "KeyError" if content is processed with labels not found.

If used on import, it puts a string 'FALLBACK_TX_STRING' in place of missing
strings.

If used on export, it replaces 'FALLBACK_TX_STRING' with the value in the
designated "fallback" translation.

On import (rw):
    Step 1:
    determine `fallback_translation` ("fallback"=True or first tx)

    Step 2:
    iterate through all the survey rows and choices and find missing keys
    or missing values (or empty strings) and fill them in with the fallback
    string

On export (fw): # PLANNED
    Step 1:
    determine `fallback_translation` ("fallback"=True or first tx)

    Step 2:
    iterate through all the survey rows and choices and find any values of
    'FALLBACK_TX_STRING' and replace with the value from the specified tx
'''

from .transformer import Transformer

TRANSLATABLE_COLS = ['label', 'hint', 'guidance_hint']
FALLBACK_TX_STRING = ''


def fill_missing_fields_in_list(rows, cols, other_anchors):
    surv = ()
    for row in rows:
        row_updates = {}
        for col in cols:
            if col not in row:
                continue
            col_updates = {}
            rowcol = row[col]
            for anchor in other_anchors:
                if anchor not in rowcol:
                    col_updates[anchor] = FALLBACK_TX_STRING
            if len(col_updates) > 0:
                row_updates[col] = rowcol.copy(**col_updates)

        if len(row_updates) > 0:
            row = row.copy(**row_updates)
        surv = surv + (row,)
    return surv


def fill_missing(choice, other_anchors):
    choice_updates = {}
    for col in TRANSLATABLE_COLS:
        if col not in choice:
            continue
        col_updates = {}
        for anchor in other_anchors:
            if _is_missing(choice[col], anchor):
                col_updates[anchor] = FALLBACK_TX_STRING
                # choice = choice.copy(**{col: FALLBACK_TX_STRING})
        if len(col_updates) > 0:
            choice_updates[col] = choice[col].copy(**col_updates)
    return choice.copy(**choice_updates)


def _is_missing(row_col, anchor):
    if anchor not in row_col:
        return True
    if row_col[anchor] is None:
        return True
    if row_col[anchor] == '':
        return True
    return False



def has_missing_fields(row_col, other_anchors):
    for anchor in other_anchors:
        if _is_missing(row_col, anchor):
            return True
    return False


def each_row_and_choice(content):
    for row in content['survey']:
        yield row
    for list_name, choices in content['choices']:
        for choice in choices:
            yield choice


def content_has_missing_fields(content, other_anchors):
    for row in each_row_and_choice(content):
        for col in TRANSLATABLE_COLS:
            if col in row and has_missing_fields(row[col], other_anchors):
                return True


class FillMissingLabels(Transformer):
    def _get_fallback_tx(self, translations):
        for tx in translations:
            if tx.get('fallback'):
                return tx
        return translations[0]

    def rw(self, content):
        translations = content.get('translations')
        if len(translations) < 2:
            return content


        fallback_tx = self._get_fallback_tx(translations)
        other_txs = filter(lambda tx: tx != fallback_tx, translations)
        other_anchors = [tx['$anchor'] for tx in other_txs]

        if not content_has_missing_fields(content, other_anchors):
            return content


        survey = fill_missing_fields_in_list(
            content['survey'],
            ['label'],
            other_anchors,
        )
        choices = {}
        for list_name, choice_list in content['choices'].items():
            clist = ()
            for choice in choice_list:
                choice = fill_missing(choice, other_anchors)
                clist = clist + (choice,)
            choices[list_name] = clist

        updates = {
            'survey': survey,
            'choices': choices,
        }
        return content.copy(**updates)

TRANSFORMER = FillMissingLabels()
