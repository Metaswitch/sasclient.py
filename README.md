# sasclient
Python SAS client library

### Usage:

```python
import metaswitch.sasclient as sasclient

# Construct and start the client. Pass in start=False and call sas.start() to start manually
sas = sasclient.Client("ellis@ellis.cw-ngv.com", "ellis", "org.projectclearwater.20151201", "sas.cw-ngv.com")

# Create a trail
trail = sasclient.Trail()

# Add markers to the trail using defined marker IDs
marker = sasclient.Marker(trail, sasclient.MARKER_ID_START)
sas.send(marker)

marker = sasclient.Marker(trail, sasclient.MARKER_ID_PRIMARY_DEVICE).add_variable_param("012345678")
sas.send(marker)

marker = sasclient.Marker(trail, sasclient.MARKER_ID_CALLING_DN).add_variable_param("012345678")
sas.send(marker)

# Send events to the trail, using event IDs from a resource pack
event = sasclient.Event(trail, 0x900001).add_static_param(80).add_variable_params(["an.example.host", "POST"])
sas.send(event)

marker = sasclient.Marker(trail, sasclient.MARKER_ID_END)
sas.send(marker)

# Close the connection and stop the client's worker thread. The thread is a daemon, so this is optional.
sas.stop()
```

### Building and testing:

make - display this readme
make env - create the environment
make test - run the unit tests
make coverage - run the unit tests with coverage

