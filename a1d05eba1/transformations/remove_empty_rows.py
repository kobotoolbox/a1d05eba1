'''
remove_empty_rows:

requires: content.schema_version == '1'

remove rows which have no meaning.
in the "survey" sheet, that means any row without a "type" value.
in the "choices" sheet, this is any row with a "list_name" value.


rw:
---------------------------
    * Iterates through "survey" and "choices" sheets to remove empty or invalid rows
    (i.e. rows with no "type" column)

    * Preserves rows which may be ruled invalid later on (e.g. unknown type)
'''

from .transformer import Transformer, TransformerRW

class RemoveEmptiesRW(Transformer):
    '''
    This prevents a blank row in the XLSForm from messing up the rest of the
    form.

    Rows are deemed "blank" if they are missing a "type" value.
    '''
    def rw__1(self, content):
        survey = self._remove_survey_rows_with_no_type(content['survey'])
        return content.copy(survey=survey)

    def _remove_survey_rows_with_no_type(self, _survey):
        survey = ()
        for row in _survey:
            if len(row) == 0:
                continue
            if row.get('type') is not None:
                survey = survey + (row,)
        return survey
