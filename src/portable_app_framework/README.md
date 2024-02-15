# Portable applications repository

A portable application is

## Usage

The application folder must contains the following files

- [config.yaml](template/config.yaml) configuration file
- [manifest.yaml](template/manifest.yaml) manifest file
- [query.rq](template/query.rq) query file

Code usage in python

```python
import pandas as pd
import brickschema
from utils.util_app import Application

app = Application(
    data=pd.DataFrame(),
    metadata=brickschema.Graph(),
    app_name='path/to/app/folder'
)
app.qualify()
app.fetch()
```

## Contribute

- Create app
- Push




