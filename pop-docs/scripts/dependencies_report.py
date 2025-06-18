import toml
import json
import requests
import argparse


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


def fetch_pypi_info(package_name):
    url = f"https://pypi.org/pypi/{package_name}/json"
    try:
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            data = response.json()
            info = data.get("info", {})
            home_page = (
                info.get("home_page") or f"https://pypi.org/project/{package_name}/"
            )
            return {
                "name": package_name,
                "description": info.get("summary", "").replace("\n", " "),
                "version": info.get("version", ""),
                "author": info.get("author", ""),
                "homepage": home_page,
                "source": "PyPI",
            }
        else:
            return default_package_info(package_name, "PyPI")
    except Exception as e:
        return default_package_info(package_name, "PyPI", f"Error fetching info: {e}")


def fetch_npm_info(package_name):
    url = f"https://registry.npmjs.org/{package_name}"
    try:
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            data = response.json()
            latest_version = data.get("dist-tags", {}).get("latest", "N/A")
            latest_info = data.get("versions", {}).get(latest_version, {})
            description = latest_info.get("description", "")
            author_info = latest_info.get("author", {})
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
                "homepage": homepage,
                "source": "NPM",
            }
        else:
            return default_package_info(package_name, "NPM")
    except Exception as e:
        return default_package_info(package_name, "NPM", f"Error fetching info: {e}")


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
        "homepage": default_url,
        "source": source,
    }


def build_markdown_table(package_infos):
    table = "| Name | Description | Version | Author | Source |\n"
    table += "|:------|:-------------|:---------|:--------|:---------|\n"
    for info in sorted(package_infos, key=lambda x: x["name"].lower()):
        name_link = f"[{info['name']}]({info['homepage']})"
        table += f"| {name_link} | {info['description']} | {info['version']} | {info['author']} | {info['source']} |\n"
    return table


def main():
    parser = argparse.ArgumentParser(
        description="Generate a markdown dependency table for PyPI and NPM packages."
    )
    parser.add_argument("--pyproject", nargs="*", help="Paths to pyproject.toml files")
    parser.add_argument("--packagejson", nargs="*", help="Paths to package.json files")
    args = parser.parse_args()

    all_package_infos = []

    if args.pyproject:
        py_deps = parse_pyproject_dependencies(args.pyproject)
        py_infos = [fetch_pypi_info(dep) for dep in py_deps]
        all_package_infos.extend(py_infos)

    if args.packagejson:
        npm_deps = parse_packagejson_dependencies(args.packagejson)
        npm_infos = [fetch_npm_info(dep) for dep in npm_deps]
        all_package_infos.extend(npm_infos)

    if not all_package_infos:
        print("No dependencies found.")
        return

    markdown_table = build_markdown_table(all_package_infos)
    print(markdown_table)


if __name__ == "__main__":
    main()
