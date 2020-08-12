from .transformations import TransformerList

from .transformations import (
    ChoicesToListFW,
    DumpExtraneousAnchorsFW,
    RemoveTranslatedFromRootFW,
    RenameKuidToAnchor,
    ReplaceTruthyStrings,
    SettingsChoicesToListFW,
    XlsformRenames,
    XlsformTranslations,
)


class ExportConfigs(TransformerList):
    schema = '2'
    transformers = ()

    def __init__(self, **kwargs):
        self.flat = kwargs.pop('flat', True)
        self.immutable = kwargs.pop('immutable', False)
        self.remove_nulls = kwargs.pop('remove_nulls', False)
        self.default_settings = kwargs.pop('default_settings', {})
        super().__init__(**kwargs)

    def fw(self, content, **kwargs):
        return self._apply_transformers(content, direction='fw', **kwargs)

class DefaultExportConfigs(ExportConfigs):
    schema = '2'
    flat = False

class DefaultExportConfigsSchema1(ExportConfigs):
    schema = '1'
    flat = True
    transformers = (
        SettingsChoicesToListFW,
    )

class XlsformExport(ExportConfigs):
    schema = '1'
    flat = True
    transformers = (
        ReplaceTruthyStrings,
        DumpExtraneousAnchorsFW,
        XlsformRenames,
        XlsformTranslations,
        RemoveTranslatedFromRootFW,
        SettingsChoicesToListFW,
    )


class KoboXlsformExport(ExportConfigs):
    schema = '1'
    flat = True
    transformers = (
        ReplaceTruthyStrings,
        RenameKuidToAnchor,
        ChoicesToListFW,
    )
