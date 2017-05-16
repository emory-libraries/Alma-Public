# Analytics MMSId
#### python version 2.7.5

#### Purpose: Get MMSIds from an Analytics report and general template for Analytics APIs

#### Dependencies: an Analytics report

----------------------------------------

### analytics_mmsid_api.py

input: configuration with:

>url=https://api-na.hosted.exlibrisgroup.com/almaws/v1/analytics/reports

>path=[your path]

>apikey=[your apikey]

>limit=1000

```
analytics_mmsid_api.py ${config} > ${output}
```

output: file of MMSIds

----------------------------------------
