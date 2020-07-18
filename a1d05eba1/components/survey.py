from ..utils.yparse import yload_file
from ..utils.kfrozendict import kfrozendict

from .base_component import SurveyComponentWithTuple, SurveyComponentWithDict
from .row import (
    Row,
    OpeningRow,
    ClosingRow,
)

from ..schema_properties import GROUPABLE_TYPES

from ..exceptions import MismatchedBeginEndGroupError, UnclosedGroupError


ROW_CONTINUE = 'ROW_CONTINUE'
ROW_BEGIN_SECTION = 'ROW_BEGIN_SECTION'
ROW_END_SECTION = 'ROW_END_SECTION'
ROW_META = 'ROW_META'


BEGIN_GROUP_TYPES = ['begin_{}'.format(t) for t in GROUPABLE_TYPES]
END_GROUP_TYPES = ['end_{}'.format(t) for t in GROUPABLE_TYPES]

FLAT_DEFAULT = True


class Surv(SurveyComponentWithTuple):
    rows = tuple()

    def load(self):
        active_parent = self
        for (_index, row_i) in enumerate(self.content.data['survey']):
            # "read_row(...)" iterates through groups as well
            for (action, subrow) in self.read_row(row_i):
                if action == ROW_META:
                    continue

                if action == ROW_BEGIN_SECTION:
                    _row = OpeningRow(content=self.content, row=subrow).set_parent(active_parent)
                elif action == ROW_END_SECTION:
                    if not hasattr(active_parent, '_parent'):
                        raise MismatchedBeginEndGroupError()
                    _row = ClosingRow().set_parent(active_parent)
                elif action == ROW_CONTINUE:
                    _row = Row(content=self.content, row=subrow).set_parent(active_parent)
                self.append(_row)

                if action == ROW_BEGIN_SECTION:
                    active_parent = _row
                elif action == ROW_END_SECTION:
                    active_parent = active_parent._parent
        if hasattr(active_parent, '_parent'):
            raise UnclosedGroupError()

    def read_row(self, row):
        _type = row['type']
        whatsit = ROW_CONTINUE
        if _type in BEGIN_GROUP_TYPES:
            whatsit = ROW_BEGIN_SECTION
        elif _type in END_GROUP_TYPES:
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

    def to_list(self, schema, flat=FLAT_DEFAULT):
        out = []
        if schema == '1':
            for meta_row in self.content.metas.items_schema1():
                out.append(meta_row)

        if flat:
            for row in self:
                out.append(row.flat_export(schema=schema))
        else:
            for row in self.rows:
                for _row in row.nested_export(schema=schema):
                    out.append(_row)


        return out
