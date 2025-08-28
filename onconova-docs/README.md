

### Generate database schema documentation.

From root of project:
```
docker compose run -v ${PWD}/onconova-docs/scripts:/app/src/scripts server python scripts/document_db.py
```


### Generate dependencies report documentation.

From root of project:
```
python onconova-docs/scripts/dependencies_report.py --pyproject server/pyproject.toml onconova-docs/pyproject.toml --packagejson onconova
-client/package.json
```