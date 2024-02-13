# Minimum OA requirement
#### Version v.1.0 (2024-01-01)
To meet the ventilation requirements, the AHU must provide a certain amount of fresh air when the building is occupied. The ventilation requirements are determined at the design stage based on the zone occupancy and other parameters. The ventilation requirements are then translated into the outdoor-air damper opening, which is generally referred to as the minimum damper position to meet ventilation requirements, typically, the minimum damper position is between 10% and 20%. If the minimum damper position is greater than 20%, more outdoor-air may be entering the building than required, and significant additional heating or cooling may be occurring at the AHU to maintain the discharge-air temperature set point

The app[^1] is structured as follows:
- Configuration file ([config.yaml](config.yaml))
- SPARQL query ([query.rq](query.rq))
- SHACL Shape or manifest ([manifest.ttl](manifest.ttl))

[^1]: by Roberto Chiosa - roberto.chiosa@polito.it 
