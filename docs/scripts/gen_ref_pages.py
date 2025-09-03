"""Generate the code reference pages."""

from pathlib import Path

import mkdocs_gen_files

root = Path(__file__).parent.parent
src = root / "../server"

for path in sorted(src.rglob("*.py")):
    try:
        module_path = path.relative_to(src).with_suffix("")
        doc_path = path.relative_to(src).with_suffix(".md")
        full_doc_path = Path("server-reference", doc_path)
        parts = tuple(module_path.parts)

        if parts[-1] in "__init__" or 'tests' in parts or 'migrations' in parts:
            continue
        elif parts[-1] == "__main__" or parts[0] != "onconova":
            continue
        with mkdocs_gen_files.open(full_doc_path, "w") as fd:
            identifier = ".".join(parts)
            print('---', file=fd)
            print(f'title: {parts[-1]}', file=fd)
            print('---', file=fd)
            print(f"<h1><code>{identifier}</code></h1>\n\n", file=fd)
            print("::: " + identifier + '\n', file=fd)
            print("    handler: python", file=fd)
            mkdocs_gen_files.set_edit_path(full_doc_path, path.relative_to(root))
    except:
        pass
