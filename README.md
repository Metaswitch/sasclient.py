# sas-client
Python SAS client library

Usage:

```python
import sas-client

...

sas-client.init(...)

trail = sas-client.Trail()

marker = sas-client.Marker(trail, ...)
# set things on the marker
marker.send()

sas-client.stop()
```