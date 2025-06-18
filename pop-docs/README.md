

### Generate database schema documentation.

From root of project:
```
docker compose run -v ${PWD}/pop-docs/scripts:/app/src/scripts  pop-server python scripts/document_db.py
```


### Generate dependencies report documentation.

From root of project:
```
python pop-docs/scripts/dependencies_report.py --pyproject pop-server/pyproject.toml pop-docs/pyproject.toml --packagejson pop
-client/package.json
```