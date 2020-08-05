from ..exceptions import (
    DuplicateAnchorError,
    MissingAnchorError,
    MissingAlternateAnchorError,
)


def pop_out_anchor(row, fallback_key, klassname):
    initial_row = row
    has_anchor = '$anchor' in row

    has_fallback = False
    if fallback_key is not None and fallback_key in row:
        has_fallback = True

    anchor = None
    if has_anchor:
        row, anchor = row.popout('$anchor')
    elif has_fallback:
        anchor = row[fallback_key]

    if not anchor:
        row_info = initial_row.unfreeze()
        if fallback_key is None:
            raise MissingAnchorError(row=row_info, klass=klassname)
        raise MissingAlternateAnchorError(row=row_info,
                                          key=fallback_key,
                                          klass=klassname)
    return (row, anchor)
