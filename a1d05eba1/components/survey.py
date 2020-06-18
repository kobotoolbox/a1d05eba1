from ..utils.yparse import yparse, yload_file, invert

from .base_component import SurveyComponentWithTuple, SurveyComponentWithDict
from .row import Row


class Surv(SurveyComponentWithTuple):
    def load(self):
        for (_index, row) in enumerate(self.content.data['survey']):
            if row['type'] not in self.content.META_TYPES:
                self.append(
                    Row(content=self.content, row=row)
                )

    def get_tx_col_names_for_v1(self):
        txcolnames = set()
        for row in self:
            txcolnames.update(row.get_row_tx_col_names_for_v1())
        return txcolnames

    def to_old_arr(self):
        out = []
        for row in self:
            out.append(row.to_old_dict())
        return out

    def to_list(self, schema):
        out = []
        if schema == '1':
            for (key, value) in self.content.metas.items():
                if value == True:
                    value = key
                out.append({
                    'type': key,
                    'name': value,
                })
        for row in self:
            out.append(row.to_export(schema=schema))
        return out
