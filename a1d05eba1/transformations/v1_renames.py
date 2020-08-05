'''
Renames survey columns from XLSForm aliases to schema-standardized columns

E,g, "media::image" becaomse "image"
'''

from .transformer import Transformer
from ..utils.yparse import yload_file

RENAMES_FROM_V1 = yload_file('renames/from1/column', invert=True)

class V1Renames(Transformer):
    def rw__1__each_row(self, row):
        renames = []
        for key in row.keys():
            if key in RENAMES_FROM_V1:
                renames.append(
                    (key, RENAMES_FROM_V1[key],)
                )
        for (_from, _to) in renames:
            row = row.renamed(_from, _to)
        return row
