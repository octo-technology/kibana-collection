```
curl -X PUT  --user elastic:changeme  "localhost:5601/api/security/role/my_kibana_role" -H 'kbn-xsrf: true' -H 'Content-Type: application/json' -d'
{
  "metadata" : {
    "version" : 1
  },
  "elasticsearch": {
    "cluster" : [ ],
    "indices" : [ ]
  },
  "kibana": [
    {
      "base": [],
      "feature": {
        "dashboard": ["read"]
      },
      "spaces": [
        "finance"
      ]
    }
  ]
}
'
```

```
curl -X POST --user elastic:changeme "localhost:9200/_security/role/my_super_simple_role?pretty" -H 'Content-Type: application/json' -d'
{
    "cluster": ["all"],
    "indices": [
    {
        "names": [ "index1" ],
        "privileges": ["all"]
    }
    ]
}
'
```

```
curl -X POST --user elastic:changeme "localhost:9200/_security/role/my_admin_role?pretty" -H 'Content-Type: application/json' -d'
{
  "cluster": ["all"],
  "indices": [
    {
      "names": [ "index1", "index2" ],
      "privileges": ["all"],
      "field_security" : { // optional
        "grant" : [ "title", "body" ]
      },
      "query": "{\"match\": {\"title\": \"foo\"}}" // optional
    }
  ],
  "applications": [
    {
      "application": "myapp",
      "privileges": [ "admin", "read" ],
      "resources": [ "*" ]
    }
  ],
  "run_as": [ "other_user" ], // optional
  "metadata" : { // optional
    "version" : 1
  }
}
'
```

```
curl -X DELETE  --user elastic:changeme  "localhost:5601/api/security/role/my_kibana_role" -H 'kbn-xsrf: true'
```
