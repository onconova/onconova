
## Installation 

1. Install compodoc

npm install -g @compodoc/compodoc

2. Install Mkdocs and dependencies

pip install .

3. Install server package 

pip install ../server

## Build full docs 

rm -rf src/compodoc/ && npx @compodoc/compodoc -p ../client/tsconfig.doc.json -d ./src/compodoc/ -y src/assets/css/compodoc/ --hideGenerator --theme material && mkdocs serve