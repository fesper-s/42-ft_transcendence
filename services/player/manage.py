#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys


def main():
    """Run administrative tasks."""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'api.settings')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == '__main__':
    main()

# Cria a api_player necessaria para fazer executar o comando python3 manage.py migrate e testar a api

# CREATE TABLE api_player (
#     id SERIAL PRIMARY KEY,
#     email VARCHAR(30) NOT NULL UNIQUE,
#     username VARCHAR(20) NOT NULL,
#     first_name VARCHAR(20) NOT NULL,
#     last_name VARCHAR(20) NOT NULL,
#     alias_name VARCHAR(20),
#     avatar VARCHAR(255) NOT NULL,
#     champions INTEGER NOT NULL DEFAULT 0,
#     wins INTEGER NOT NULL DEFAULT 0,
#     losses INTEGER NOT NULL DEFAULT 0,
#     two_factor BOOLEAN NOT NULL DEFAULT False,
#     status VARCHAR(2) NOT NULL DEFAULT 'OF',
#     password VARCHAR(10) NOT NULL,
#     last_login DATE
# );
