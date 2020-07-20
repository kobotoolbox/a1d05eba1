import re

from ..utils.kfrozendict import kfrozendict

TAG_COLS = ['hxl']


def _expand_tags(**row):
    tags = ()
    main_tags = row.get('tags', ())
    if len(main_tags) > 0:
        tags = tuple(main_tags)

    for tag_col in TAG_COLS:
        tags_str = row.get(tag_col)
        if tags_str and isinstance(tags_str, str):
            for tag in re.findall(r'([\#\+][a-zA-Z][a-zA-Z0-9_]*)', tags_str):
                tags = tags + ('hxl:%s' % tag,)
    return tags


class TagsField:
    ROW_KEYS = {
        # by schema
        '1': ['hxl', 'tags'],
        '2': ['tags'],
    }
    EXPORT_KEY = 'tags'

    @classmethod
    def in_row(kls, row, schema):
        return (
            'hxl' in row or 'tags' in row
        )

    @classmethod
    def pull_from_row(kls, row, content):
        (row, _hxl) = row.popout('hxl', '')
        (row, _tags) = row.popout('tags', ())
        if isinstance(_tags, str):
            _tags = tuple([_tags])
        tags = _expand_tags(hxl=_hxl, tags=_tags)
        yield kls(content, tags)

    def __init__(self, content, tags):
        self.content = content
        self.key = 'tags'
        self.tags = tags

    def dict_key_vals_old(self, renames=None):
        tags = {'hxl': [], 'tags': []}
        for tag in self.tags:
            mtch = re.match('^hxl:(.+)$', tag)
            if mtch:
                tags['hxl'].append(mtch.group(1))
            else:
                tags['tags'].append(tag)
        for col in ['hxl', 'tags']:
            if len(tags[col]) > 0:
                yield (col, ' '.join(tags[col]))
        if len(tags['hxl']) > 0:
            yield ('hxl', ' '.join(tags['hxl']))

    def dict_key_vals_new(self):
        return ('tags', self.tags)
