
class SchemaError(ValueError):
    pass

class TranslationImportError(ValueError):
    pass

class SchemaRefError(ImportError):
    pass

class StructureError(ValueError):
    pass

class MismatchedBeginEndGroupError(StructureError):
    pass

class UnclosedGroupError(MismatchedBeginEndGroupError):
    pass
