[//]: # (AUTOMATICALLY GENERATED DO NOT MODIFY)

# AHU Variables Check

#### Version v.1.0 (2024-01-01)

Look for the following points in the metadata schema Cooling_Command, Damper_Position_Command, Heating_Command, Supply_Air_Temperature_Setpoint, Outside_Air_Temperature_Sensor, Return_Air_Temperature_Sensor, Mixed_Air_Temperature_Sensor, Supply_Air_Temperature_Sensor

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
    app_name='app_check_variables'
)
app.qualify()
app.fetch()
app.clean()
app.analyze()
```

[^1]: by Roberto Chiosa - roberto.chiosa@polito.it 
