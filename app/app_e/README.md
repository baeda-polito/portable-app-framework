[//]: # (AUTOMATICALLY GENERATED DO NOT MODIFY)

# App name

#### Version v.1.0 (YYYY-MM-DD)

Short description

## Structure

The app[^1] is structured as follows:

- Configuration file ([config.yaml](config.yaml))
- SPARQL query ([query.rq](query.rq))
- SHACL Shape or manifest ([manifest.ttl](manifest.ttl))
- Preprocess function ([preprocess.py](preprocess.py))
- Analyze function ([analyze.py](analyze.py))


The app accepts the following parameters

- `time_from` 2021-01-01 00:00:00+00:00
- `time_to` 2021-01-01 00:00:00+00:00
- `aggregation` 1h

## Usage

```python
import pandas as pd
import brickschema
from portable_app_framework import Application

app = Application(
    metadata=brickschema.Graph(),
    app_name='app_e'
)
qualify_result = app.qualify() # True/False
fetch_result = app.fetch() # Dict of mapped variables
df = pd.DataFrame()# get df according to your logic 
df_preprocess = app.preprocess(df)
final_result = app.analyze(df_preprocess)
```

[^1]: by Author Name - example@mail.com 
