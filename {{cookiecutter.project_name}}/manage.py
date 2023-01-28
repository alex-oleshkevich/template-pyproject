#!/usr/bin/env python
import runpy

if __name__ == "__main__":
    """
    Execute command line interface.

    Usage:
        cd {{cookiecutter.project_name}}/
        python manage.py

    This is equivalent to `python -m {{cookiecutter.project_name}}`
    """
    runpy.run_module("{{cookiecutter.project_name}}", run_name="__main__")
