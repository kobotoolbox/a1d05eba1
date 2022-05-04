# SCHEMA FOR ASSET.CONTENT (XLSFORM-STYLED DOCUMENTS)

## "what is this project?"

The name is a jumble of characters while we decide what the project actually
*does* and what it should be named.

### The problem:

All survey-related components of `kobotoolbox/kpi` which reference XLSForm-style
content within a survey must constantly check types and replace aliases. There
is no consistency even within our own applications because the structure has
evolved and the tools (especially the form builder) has remained stagnant.

Inside the survey, internal references (e.g. skip logic) are not validated and
can easily break.

To address these problems, this project puts forward a way to generate and migrate
`asset.content` from existing structures and aliases to a similar structure defined
with the form's logic in mind. (examples to come)

### The code herein...

Initial efforts have been focused on ensuring that all existing features of
KoBoToolbox KPI can continue to work while new features can be built around
the structured content.

As such, the code is currently focused on:

* Migrating surveys back and forth from `schema:'1'` to `schema:'2'` so that
  content can be stored in the database in the validated structure, and the existing
  tools like the form builder and XLS will still work as expected.
* A valid [json-schema](https://json-schema.org/) is generated from the YML
  files in this project which can be used by `kobotoolbox/kpi` in order to
  validate content on save and report broken forms so that we can fix issues
  during development.

## Using this to migrate forms:

A `Content` object loads in a survey structure and applies "transformers" to
the content to make sure everything is in the format that the inner code needs.

See `content_variations.py` for some examples of subclasses and transformers.

## Viewing the SCHEMA

from a1d05eba1 import MAIN_JSONSCHEMA
pprint(MAIN_JSONSCHEMA)

## Changing SCHEMA

The SCHEMA document (a valid json-schema per DraftVersion6) is generated from a
collection of YAML files.

## Migrating an XLSForm to this schema

XLSForm is not yet supported, but the structure stored in kobotoolbox/kpi's
asset.content (which loosely resembles an XLSForm) is supported. That structure
has an attribute `"schema":"1"`. This is how one would migrate an asset of that
structure to the new validated structure:

```
from a1d05eba1.content import Content
my_asset_content = {...} # pulled from kpi.models.Asset's content
assert my_asset_content['schema'] == '1' # as set in kpi.models.Asset
jsonschema_validated = Content(my_asset_content).export(schema='2')
```

## Running tests

1. Create and activate a new virtualenv, then:

```
pip install -r dev-requirements.txt
py.test -sx
# or generate coverage report:
pytest --cov=a1d05eba1 tests/ --cov-report=html
```
