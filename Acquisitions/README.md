# Acquistions API Scripts

### Contributors: Alex Cooper

### Date: 09/22/2017

### Purpose: API scripts to retrieve, modify, and create acquisitions records

---

## get_order_line_api.py

#### Purpose: Retrieve POL record from Alma

```
$get_order_line_api.py [po_line_id]
```

#### Dependencies: Needs a configuration file

```
get_po_line_url=[Alma url]
apikey=[your apikey]
```

---

## create_order_line_api.py

#### Purpose: Create POL record fpr Alma

```
$create_order_line_api.py
```

#### Dependencies: Needs a configuration file

```
create_po_line_url=[Alma url]
get_po_line_url=[Alma url]
apikey=[your apikey]
```

#### And requires an [order xml](https://github.com/Emory-LCS/Alma-Public/blob/master/Acquisitions/files/create_order.xml)

---

