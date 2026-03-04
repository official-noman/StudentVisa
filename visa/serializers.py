from rest_framework import serializers
from .models import Thana
from django.core.serializers.json import DjangoJSONEncoder
from django.core.serializers import serialize
from django.db.models import Model
import json
class ThanaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Thana
        fields = ['id', 'name']



class ModelJSONEncoder(DjangoJSONEncoder):
    def default(self, o):
        if isinstance(o, Model):
            # Serialize the model to JSON using Django's serialize function
            return json.loads(serialize('json', [o]))[0]['fields']
        return super().default(o)