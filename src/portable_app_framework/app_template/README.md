[//]: # (AUTOMATICALLY GENERATED DO NOT MODIFY)

# App Template

#### Version v.1.0 (YYYY-MM-DD)

Short description

## Structure

The app[^1] is structured as follows:

- Configuration file ([config.yaml](config.yaml))
- SPARQL query ([query.rq](query.rq))
- SHACL Shape or manifest ([manifest.ttl](manifest.ttl))

## Usage

```python
import pandas as pd
import brickschema
from portable_app_framework import Application

app = Application(
    metadata=brickschema.Graph(),
    app_name='app_template'
)
app.qualify()
app.fetch()
app.clean()
app.analyze()
```

[^1]: by Author Name - example@mail.com 
