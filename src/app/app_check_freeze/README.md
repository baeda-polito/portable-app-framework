[//]: # (AUTOMATICALLY GENERATED DO NOT MODIFY)

# Freeze prevention check

#### Version v.1.0 (2024-01-01)

The outdoor-air damper should be locked out to the minimum position for freeze prevention when the outdoor-air temperature is below 40 F (4 ◦C), and the outdoor-air dampers should be completely closed if the mixed-air temperature becomes lower than 40oF. Given that from the previous check it is possible to automatically extract the minimum OA we can check that in such conditions the damper is at minimum or closed.

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
    app_name='app_check_freeze'
)
app.qualify()
app.fetch()
app.clean()
app.analyze()
```

[^1]: by Roberto Chiosa - roberto.chiosa@polito.it 
