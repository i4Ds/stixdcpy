sdcpy provides you APIs to access various data on STIX data center and basic tools to analyzer the data.  
sdcpy is still under development. 



Example 
```python
from sdc import QuickLook
lc=QuickLook.LightCurves('2021-05-07T00:00:00', '2021-05-08T00:00:00', ltc=True)
lc.peek()
```
