# Portable applications framework package

This folder contains the source code for the portable applications framework package. The package is designed to
facilitate the development of portable applications that can be easily shared and reused.

## Structure

```txt
├── README.md
├── __init__.py                   # Package initialization with Application class and CLI
├── app_template                  # Template example application
│   ├── README.md           
│   ├── __init__.py               # Application initialization
│   ├── config.yaml               # Application configuration
│   ├── manifest.ttl              # SHACL Shape or manifest
│   └── query.rq                  # SPARQL query
├── libraries                     # External libraries
│   ├── Brick-nightly.ttl
│   ├── Brick-subset.ttl
│   ├── Brick.ttl
│   └── constraints.ttl    
└── utils                         # Utility functions
    ├── logger.py                 # Logging utility
    ├── util.py                   # General utility functions
    ├── util_brick.py             # Brick-specific utility functions
    └── util_qualify.py           # Qualification utility functions
```
