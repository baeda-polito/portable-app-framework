# Portable applications repository

A portable application is

Available apps are:

- [app_check_freeze](app_check_freeze)
- [app_check_min_oa](app_check_min_oa)
- [app_check_sensor](app_check_sensor)
- [app_check_variables](app_check_variables)
- [app_example](app_example)
- [app_preprocessing](app_preprocessing)

## Usage

The application folder must contains the following files

- [config.yaml](app_example/config.yaml) configuration file
- [manifest.yaml](app_example/manifest.yaml) manifest file
- [query.rq](app_example/query.rq) query file

Code usage in python

```python
import pandas as pd
import brickschema
from utils.util_app import Application

app = Application(
    data=pd.DataFrame(),
    metadata=brickschema.Graph(),
    config_folder='path/to/app/folder'
)
app.qualify()
app.fetch()
```

## Contribute

- Create app
- Push




