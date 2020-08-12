def strip(ds):
    return '\n'.join([l.strip() for l in ds.strip().split('\n')])

class BaseValueError(ValueError):
    # subclasses of "BaseValueError" have messages defined in the docstring
    def __init__(self, *args, **kwargs):
        super().__init__(strip(self.__doc__.format(*args, **kwargs)))

class SchemaError(BaseValueError):
    ''

class TranslationImportError(BaseValueError):
    ''

class DirectionalTransformerError(BaseValueError):
    '''
    Cannot call {a1} on a {a2} transformer. [{name}]
    '''

class SchemaRefError(ImportError):
    pass

class StructureError(BaseValueError):
    '''
    Survey content structure error. {message}
    '''

class MismatchedBeginEndGroupError(StructureError):
    '''
    More row groupings were closed than exist in the form
    '''

class UnclosedGroupError(MismatchedBeginEndGroupError):
    '''
    A row grouping (type="{0}") was opened but not closed.
    '''

class MissingAnchorError(BaseValueError):
    '''
    {klass}({row}) needs a specified "$anchor"
    '''

class MissingAlternateAnchorError(BaseValueError):
    '''
    {klass}({row}) needs a specified "{key}" or "$anchor"
    '''

class DuplicateAnchorError(BaseValueError):
    '''
    {klass} specified "{key}" or "$anchor" must be unique
    CONFLICTS:
    - {row1}
    - {row2}
    '''


from jsonschema.exceptions import ValidationError

class SchemaValidationError(ValidationError):
    pass
