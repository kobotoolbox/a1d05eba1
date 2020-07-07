from ..utils.yparse import yload_file
from ..utils.kfrozendict import kfrozendict

from .base_component import SurveyComponentWithTuple, SurveyComponentWithDict
from .row import (
    Row,
    OpeningRow,
    ClosingRow,
)

ROW_CONTINUE = 'ROW_CONTINUE'
ROW_BEGIN_SECTION = 'ROW_BEGIN_SECTION'
ROW_END_SECTION = 'ROW_END_SECTION'
ROW_META = 'ROW_META'

FLAT_DEFAULT = True


class Surv(SurveyComponentWithTuple):
    rows = tuple()

    def load(self):
        active_parent = self
        for (_index, zrow) in enumerate(self.content.data['survey']):
            # "read_row(...)" iterates through groups
            for (action, subrow) in self.read_row(zrow):

                if action == ROW_META:
                    continue

                if action == ROW_BEGIN_SECTION:
                    _row = OpeningRow(content=self.content, row=subrow).set_parent(active_parent)
                elif action == ROW_END_SECTION:
                    _row = ClosingRow().set_parent(active_parent)
                elif action == ROW_CONTINUE:
                    _row = Row(content=self.content, row=subrow).set_parent(active_parent)
                self.append(_row)

                if action == ROW_BEGIN_SECTION:
                    active_parent = _row
                elif action == ROW_END_SECTION:
                    if active_parent._parent == None:
                        raise ValueError('Unmatched BEGIN and END of group')
                    active_parent = active_parent._parent

    def read_row(self, row):
        _type = row['type']
        whatsit = ROW_CONTINUE
        if _type in ['begin_group']:
            whatsit = ROW_BEGIN_SECTION
        elif _type in ['end_group']:
            whatsit = ROW_END_SECTION
        elif _type in self.content.META_TYPES:
            whatsit = ROW_META

        if 'rows' not in row:
            yield (whatsit, row)
        else:
            for subrow in self.read_group(row):
                yield subrow

    def read_group(self, group):
        (group, rows) = group.popout('rows')
        yield (ROW_BEGIN_SECTION, group)
        for row in rows:
            for subrow in self.read_row(row):
                yield subrow
        yield (ROW_END_SECTION, group)

    def get_tx_col_names_for_v1(self):
        txcolnames = set()
        for row in self:
            txcolnames.update(row.get_row_tx_col_names_for_v1())
        return txcolnames

    def to_list(self, schema, flat=FLAT_DEFAULT):
        out = []
        if schema == '1':
            for (key, value) in self.content.metas.items():
                if value == True:
                    value = key
                out.append({
                    'type': key,
                    'name': value,
                })

        if flat:
            for row in self:
                out.append(row.to_flat_export(schema=schema))
        else:
            for row in self.rows:
                for deets in row.oy_unflat_export(schema=schema):
                    out.append(deets)


        return out
