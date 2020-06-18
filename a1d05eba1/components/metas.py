from ..utils.kfrozendict import kfrozendict

from .base_component import SurveyComponentWithDict


class Metas(SurveyComponentWithDict):
    def load(self):
        self._any = False
        if self.content.schema == '1':
            metas = {}
            survey = []
            for row in self.content.data.get('survey', []):
                if row.get('type') in self.content.META_TYPES:
                    value = row['name']
                    if row['name'] == row['type']:
                        value = True
                    metas[row['type']] = value
            if len(metas) > 0:
                self._any = True
            self._d = kfrozendict.freeze(metas)
        else:
            _settings = self.content.data['settings']
            metas = _settings.get('metas', {})
            if len(metas) > 0:
                self._any = True
            self._d = kfrozendict.freeze(metas)

    def items(self):
        return self._d.items()

    def any(self):
        return self._any

    def to_dict(self):
        return kfrozendict.unfreeze(self._d)
