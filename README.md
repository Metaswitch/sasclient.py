# sas-client
Python SAS client library

Usage:

```python
import sas-client

...

sas-client.init(...)

trail = sas-client.new_trail()

marker = sas-client.Marker()
# set things on the marker
marker.send()

sas-client.stop()
```