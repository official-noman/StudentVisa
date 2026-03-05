import os

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "studentvisabd.settings")
import django

django.setup()
from django.db import connection

conn = connection._connections["default"]
print("INSTANCE VAR:", vars(conn).get("data_types_suffix"))
print("MRO CHECK:")
for cls in type(conn).__mro__:
    if "data_types_suffix" in vars(cls):
        val = vars(cls)["data_types_suffix"]
        print(cls, type(val), repr(val))
