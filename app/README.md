# Portable applications repository

A portable application is

Available apps are:

- app_check_freeze
- app_check_stuck_damper
- app_check_stuck_valve

## Usage

The application folder must contains the following files

- [config.yaml](app_example/config.yaml) configuration file
- [manifest.yaml](app_example/manifest.yaml) manifest file
- [query.rq](app_example/query.rq) query file

Code usage in python

```python
folder = 'path/to/app/folder'
app = Application(data=df, metadata=graph, config_folder=folder)
app.qualify()
app.fetch()
app.res.result, app.res.message = check_sensor(app.res.data, config)
```

## Contribute

- Create app
- Push




