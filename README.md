# sasclient
Python SAS client library

Usage:

```python
import metaswitch.sasclient as sasclient

sasclient.start("ellis@ellis.cw-ngv.com", "ellis", "org.projectclearwater.20151201", "sas.cw-ngv.com")

trail = sasclient.Trail()

marker = sasclient.Marker(trail, sasclient.MARKER_ID_START)
sasclient.send(marker)

marker = sasclient.Marker(trail, sasclient.MARKER_ID_PRIMARY_DEVICE).add_variable_params(["012345678"])
sasclient.send(marker)

event = sasclient.Event(trail, 0x900001).add_static_params([80]).add_variable_params(["an.example.host"])
sasclient.send(event)

marker = sasclient.Marker(trail, sasclient.MARKER_ID_END)
sasclient.send(marker)

sasclient.stop()
```




