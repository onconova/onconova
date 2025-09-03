import json
from pathlib import Path
from typing import Any, Optional

from django.core.management.base import BaseCommand, CommandError, CommandParser
from django.urls.base import resolve
from django.utils.module_loading import import_string
from ninja.main import NinjaAPI
from ninja.management.utils import command_docstring
from ninja.responses import NinjaJSONEncoder


class Command(BaseCommand):
    """
    Django management command to export the OpenAPI schema from a NinjaAPI instance.

    This command allows you to export the OpenAPI schema for your API, either to stdout or to a specified file.
    You can specify the API instance to use, customize the JSON output formatting, and control key sorting and ASCII encoding.

    Options:
        --api           Specify the import path to the NinjaAPI instance (default: 'onconova.api.api').
        --output        Output the schema to a file (if omitted, outputs to stdout).
        --indent        Indent level for pretty-printing the JSON output.
        --sorted        Sort the JSON keys alphabetically.
        --ensure-ascii  Ensure ASCII encoding for the JSON output.

    Example usage:
        python manage.py export_openapi_schema --api project.urls.api --output schema.json --indent 2 --sorted
    """

    help = "Exports Open API schema"

    def _get_api_instance(self, api_path: Optional[str] = None) -> NinjaAPI:
        if not api_path:
            try:
                return resolve("/api/").func.keywords["api"]  # type: ignore
            except AttributeError:
                raise CommandError(
                    "No NinjaAPI instance found; please specify one with --api"
                ) from None

        try:
            api = import_string(api_path)
        except ImportError:
            raise CommandError(
                f"Module or attribute for {api_path} not found!"
            ) from None

        if not isinstance(api, NinjaAPI):
            raise CommandError(f"{api_path} is not instance of NinjaAPI!")

        return api

    def add_arguments(self, parser: CommandParser) -> None:
        parser.add_argument(
            "--api",
            dest="api",
            default="onconova.api.api",
            type=str,
            help="Specify api instance module",
        )
        parser.add_argument(
            "--output",
            dest="output",
            default=None,
            type=str,
            help="Output schema to a file (outputs to stdout if omitted).",
        )
        parser.add_argument(
            "--indent", dest="indent", default=None, type=int, help="JSON indent"
        )
        parser.add_argument(
            "--sorted",
            dest="sort_keys",
            default=False,
            action="store_true",
            help="Sort Json keys",
        )
        parser.add_argument(
            "--ensure-ascii",
            dest="ensure_ascii",
            default=False,
            action="store_true",
            help="ensure_ascii for JSON output",
        )

    def handle(self, *args: Any, **options: Any) -> None:
        api = self._get_api_instance(options["api"])
        schema = api.get_openapi_schema()
        result = json.dumps(
            schema,
            cls=NinjaJSONEncoder,
            indent=options["indent"],
            sort_keys=options["sort_keys"],
            ensure_ascii=options["ensure_ascii"],
        )

        if options["output"]:
            with Path(options["output"]).open("wb") as f:
                f.write(result.encode())
        else:
            self.stdout.write(result)


__doc__ = command_docstring(Command)
