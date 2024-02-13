[//]: # (AUTOMATICALLY GENERATED DO NOT MODIFY)

# Check Variables

#### Version v.1.0 (2024-01-01)

Checks if are there any stuck sensor. The analysis is performed depending on the type of sensor/point.

## Structure

The app[^1] is structured as follows:

- Configuration file ([config.yaml](config.yaml))
- SPARQL query ([query.rq](query.rq))
- SHACL Shape or manifest ([manifest.ttl](manifest.ttl))


## Usage

```python
import pandas as pd
import brickschema
from afdd_framework import Application

app = Application(
    data=pd.DataFrame(),
    metadata=brickschema.Graph(),
    app_name='app_check_sensor'
)
app.qualify()
app.fetch()
app.clean()
app.analyze()
```

[^1]: by Roberto Chiosa - roberto.chiosa@polito.it 
