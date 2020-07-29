'''
xlsform_metas_to_settings:

pull "meta" questions out of the survey and put them into their own
sheet
'''

from ..utils.yparse import yload_file
from .transformer import Transformer


from ..schema_properties import META_PROPERTIES

XLSFORM_RENAMED_METAS = yload_file('renames/from1/metas', invert=True)


class MetasToSurveyRoot(Transformer):
    def rw(self, content):
        updates = {}
        survey = tuple()
        metas = tuple()
        for row in content.get('survey', []):
            (row, is_meta) = self.rw__each_row_extract_metas(row)

            if is_meta:
                metas = metas + (row,)
            else:
                survey = survey + (row,)

        if len(metas) > 0:
            updates['survey'] = survey
            metas_dict = {}
            for meta in metas:
                (meta, _type) = meta.popout('type')
                metas_dict[_type] = meta
            updates['metas'] = metas_dict

        return content.copy(**updates)

    def rw__each_row_extract_metas(self, row):
        _type = row['type']
        is_meta = False
        if _type in XLSFORM_RENAMED_METAS:
            _type = XLSFORM_RENAMED_METAS[_type]
            row = row.copy(type=_type)
        if _type in META_PROPERTIES:
            is_meta = True
        return (row, is_meta)

TRANSFORMER = MetasToSurveyRoot()
