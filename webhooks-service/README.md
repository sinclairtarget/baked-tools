# Baked Webhooks Service
This is a Flask web application responsible for handling webhook calls from
Shotgrid.

As of this writing, here are the routes/endpoints supported by the application:

```
Endpoint                             Methods  Rule
-----------------------------------  -------  --------------------------------
health.ping                          GET      /ping
sheets.trigger_sync                  POST     /webhooks/sheets/sync
static                               GET      /static/<path:filename>
status.handle_shot_status_change     POST     /webhooks/status/shot
status.handle_task_status_change     POST     /webhooks/status/task
status.handle_version_created        POST     /webhooks/status/version-created
status.handle_version_status_change  POST     /webhooks/status/version
```

## Running the Application Locally
You can run the application locally on your own computer. It will listen for
incoming connections at your local address.

In order to run the application, you first have to install the Python
dependencies.

### Python Dependencies
Create a virtual environment. This will be the environment into which you
install the Python dependencies.

You can do this like so:
```
$ python -m venv venv
```

Enter the virtual environment:
```
$ source ./venv/bin/activate
```

Install `pip-tools`:
```
$ pip install pip-tools
```

Use `pip-tools` to sync the dependencies:
```
$ pip-sync requirements.txt dev-requirements.txt
```

You can exit the virtual environment by running `deactivate`.

### Running
Once you've install the necessary dependencies, you can start the server by
running:

```
$ FLASK_APP=service SHOTGRID_SECRET_TOKEN=foobar SHOTGRID_API_KEY=foobar flask run
```

See below for information about environment variables.

By default, the server will start listening for incoming connections on port
5000. You can test it out by going to the following address in your browser:
`http://localhost:5000/ping`

### Environment Variables
The application cares about the following environment variables:

| Variable Name | Purpose |
|---|---|
| `FLASK_APP` | This should always be set to `service`. It helps Flask find the application to run. |
| `SHOTGRID_API_KEY` | This should be set to the API key we use for Shotgrid. |
| `SHOTGRID_SECRET_TOKEN` | This is used to check that incoming requests are really from Shotgrid. |

`SHOTGRID_SECRET_TOKEN` is an environment variable that you can set to whatever
you want when you're running the server locally. In production, it must be set
to the actual secret token.

## Development
The Flask application is created in
[./service/__init__.py](./service/__init__.py).

The various routes exposed by the web application are defined under
[./service/routes](./service/routes).

The logic for loading the `status_mapping.yaml` file can be found in
[./service/lib/config.py](./service/lib/config.py).

The important code for interacting with the Shotgrid API can be found in
[./service/lib/sg.py](./service/lib/sg.py).
