```
curl -X POST --user elastic:changeme "localhost:9200/_security/role/my_simple_role?pretty" -H 'Content-Type: application/json' -d'
{
    "cluster": ["all"],
    "indices": [
    {
        "names": [ "index1" ],
        "privileges": ["all"]
    }
    ],
    "applications": [
    {
        "application": "myapp",
        "privileges": [ "admin", "read" ],
        "resources": [ "*" ]
    }
    ]
}
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
