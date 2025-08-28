#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import contextlib
import os
import sys

import pghistory


def main():
    """Run administrative tasks."""
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "onconova.settings")
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc

    if (
        len(sys.argv) > 1
        and not sys.argv[1].startswith("runserver")
        and sys.argv[1] not in ["migrate", "test"]
    ):
        # Group history context under the same management command if
        # we aren't running a server or running migration during migrate
        # or test command.
        history_context = pghistory.context(command=sys.argv[1])
    else:
        history_context = contextlib.ExitStack()

    with history_context:
        execute_from_command_line(sys.argv)


if __name__ == "__main__":
    main()
    main()
