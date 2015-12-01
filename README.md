# sas-client
Python SAS client library

Usage:

```python
import metaswitch.sasclient as sasclient

sasclient.start("ellis@ellis.cw-ngv.com", "ellis", "org.projectclearwater.20151201", "sas.cw-ngv.com")

trail = sasclient.Trail()

marker = sasclient.Marker(trail, ...)
# set things on the marker

sasclient.send(marker)

sasclient.stop()
```
