import json

from pathlib import Path
import requests
import toml

import mkdocs_gen_files
import re

def parse_pyproject_dependencies(paths):
    dependencies = set()
    for path in paths:
        try:
            with open(path, "r") as file:
                data = toml.load(file)
                project = data.get("tool", {}).get("poetry", {})

                deps = project.get("dependencies", [])
                dependencies.update(parse_dependency_names(deps))

                optional_deps = project.get("optional-dependencies", {})
                for group in optional_deps.values():
                    dependencies.update(parse_dependency_names(group))
        except Exception as e:
            print(f"Error reading {path}: {e}")
    return dependencies


def parse_dependency_names(dependency_list):
    names = set()
    for dep in dependency_list:
        name = dep.split(" ")[0].split(";")[0].split("[")[0]
        names.add(name)
    return names


def parse_packagejson_dependencies(paths):
    dependencies = set()
    for path in paths:
        try:
            with open(path, "r") as file:
                data = json.load(file)
                deps = data.get("dependencies", {})
                dev_deps = data.get("devDependencies", {})
                dependencies.update(deps.keys())
                dependencies.update(dev_deps.keys())
        except Exception as e:
            print(f"Error reading {path}: {e}")
    return dependencies


def _get_pypi_license(data) -> str:
    license_field = data.get("license-expression", data.get("license", ""))

    if license_field:
        license_name = (
            license_field
            if isinstance(license_field, str)
            else " + ".join(license_field)
        )
    check_classifiers = (
        not license_field
        or license_name
        in (
            "UNKNOWN",
            "Dual License",
            "",
            None,
        )
        or license_name.count("\n")
    )
    if check_classifiers:
        license_names = [
            classifier.rsplit("::", 1)[1].strip()
            for classifier in data["classifiers"]
            if classifier.startswith("License ::")
        ]
        license_name = " + ".join(license_names)
    return license_name or "Unknown"


def fetch_pypi_info(package_name):
    url = f"https://pypi.org/pypi/{package_name}/json"
    response = requests.get(url, timeout=5)
    if response.status_code == 200:
        data = response.json()
        info = data.get("info", {})
        home_page = info.get("home_page") or f"https://pypi.org/project/{package_name}/"
        return {
            "name": package_name,
            "description": info.get("summary", "").replace("\n", " "),
            "version": info.get("version", ""),
            "license": _get_pypi_license(info),
            "author": info.get("author", ""),
            "homepage": home_page,
            "source": "PyPI",
        }
    else:
        return default_package_info(package_name, "PyPI")


def fetch_npm_info(package_name):
    url = f"https://registry.npmjs.org/{package_name}"
    response = requests.get(url, timeout=5)
    if response.status_code == 200:
        data = response.json()
        latest_version = data.get("dist-tags", {}).get("latest", "N/A")
        latest_info = data.get("versions", {}).get(latest_version, {})
        description = latest_info.get("description", "")
        description = re.sub(r"<[^>]*>.*?</[^>]*>", "", description, flags=re.DOTALL)
        description = re.sub(r"<.*?>", "", description)
        author_info = latest_info.get("author", {})
        license = latest_info.get("license", "Unknown")
        author = (
            author_info.get("name")
            if isinstance(author_info, dict)
            else author_info or "N/A"
        )
        homepage = latest_info.get(
            "homepage", f"https://www.npmjs.com/package/{package_name}"
        )
        return {
            "name": package_name,
            "description": description,
            "version": latest_version,
            "author": author,
            "license": license,
            "homepage": homepage,
            "source": "NPM",
        }
    else:
        return default_package_info(package_name, "NPM")


def default_package_info(name, source, description="Not found"):
    default_url = (
        f"https://pypi.org/project/{name}/"
        if source == "PyPI"
        else f"https://www.npmjs.com/package/{name}"
    )
    return {
        "name": name,
        "description": description,
        "version": "N/A",
        "author": "N/A",
        "license": "Unknown",
        "homepage": default_url,
        "source": source,
    }


def build_markdown_table(package_infos):
    table = "| Name | Description | Version | Author | License | Source |\n"
    table += "|:------|:-------------|:---------|:--------|:---------|:-------|\n"
    for info in sorted(package_infos, key=lambda x: x["name"].lower()):
        name_link = f"[{info['name']}]({info['homepage']})"
        table += f"| {name_link} | {info['description']} | {info['version']} | {info['author']} | {info['license']} | {info['source']} |\n"
    return table


root = Path(__file__).parent.parent
src = root / "src" 

pyproject = ['../server/pyproject.toml', './pyproject.toml']
packagejson = ['../client/package.json']
all_package_infos = []

py_deps = parse_pyproject_dependencies(pyproject)
py_infos = [fetch_pypi_info(dep) for dep in py_deps]
all_package_infos.extend(py_infos)


npm_deps = parse_packagejson_dependencies(packagejson)
npm_infos = [fetch_npm_info(dep) for dep in npm_deps]
all_package_infos.extend(npm_infos)

if not all_package_infos:
    raise RuntimeError('No dependencies found.')

markdown_table = build_markdown_table(all_package_infos)

with open(Path(src, 'credits.md'), "r") as f:
    with mkdocs_gen_files.open(Path("credits.md"), "w") as fd:
        print(f.read().replace("::autogenerated-dependencies-table", markdown_table), file=fd)
