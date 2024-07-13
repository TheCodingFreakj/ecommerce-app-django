import os
import sys
from django.core.management import execute_from_command_line

if __name__ == "__main__":
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "user_service.settings")

    try:
        # Run `makemigrations`
        execute_from_command_line([sys.argv[0], "makemigrations"])
        # Run `migrate`
        execute_from_command_line([sys.argv[0], "migrate"])
    except Exception as e:
        print(f"An error occurred: {e}")
