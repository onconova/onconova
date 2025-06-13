

### Generate database schema documentation.

From root of project:
```
docker compose run -v ${PWD}/pop-docs/scripts:/app/src/scripts  pop-server python scripts/document_db.py
```