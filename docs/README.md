# Mkdocs Onconova Documentation 

## Installation 

1. Install compodoc

```shell
npm install -g @compodoc/compodoc
```

2. Install Mkdocs and dependencies

```shell
pip install .
```

3. Install server package 

```shell
pip install ../server
```

## Build full docs 

```shell
rm -rf src/compodoc/ && rm -rf src/fhir-ig && \
npx @compodoc/compodoc -p ../client/tsconfig.doc.json -d ./src/compodoc/ -y src/assets/css/compodoc/ --hideGenerator --theme material && \
mkdocs serve
```