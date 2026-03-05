import os

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "studentvisabd.settings")

import django

django.setup()

from django.db import connection

print("DATA TYPES SUFFIX:", repr(connection.data_types_suffix))
print("TYPE:", type(connection.data_types_suffix))
