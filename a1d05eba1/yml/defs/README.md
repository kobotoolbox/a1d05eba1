## Base schemas

survey.yml
choices.yml
translations.yml
settings.yml


## Partial schemas

These are reused in different areas. They are referenced in other schemas by
a "$ref". For example:

```
{ $ref: '#/$defs/surveyRow' }
```

will pull the file `_surveyRow.yml` and add it to the `$defs` section of the
schema.

These are the current "partials":

_alphanumericValue.yml
_booleanOrString.yml
_booleanOrXpath.yml
_choice.yml
_fileCode.yml
_settingsMetas.yml
_surveyRowType.yml
_surveyRow.yml
_translatableMedia.yml
_translatable.yml
_translationsItem.yml
_webUrl.yml
_xpath.yml
