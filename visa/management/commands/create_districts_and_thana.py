import json, os
from django.core.management.base import BaseCommand
from visa.models import District, Thana

class Command(BaseCommand):
    help = 'Populate Districts and Thana models with data from JSON files'

    def handle(self, *args, **options):
        json_district_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../static/assets/json/districts.json'))
        json_thana_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../static/assets/json/thana.json'))
        with open(json_district_path) as f:
            districts_data = json.load(f)['districts']

        with open(json_thana_path) as f:
            thana_data = json.load(f)['thana']

        # Populate District model
        for district in districts_data:
            District.objects.create(
                id=int(district['id']),
                name=district['name'],
                lat=district['lat'],
                lon=district['lon'],
                website=district['url']
            )

        # Populate Thana model
        for thana in thana_data:
            district_id = int(thana['district_id'])
            district = District.objects.get(id=district_id)
            Thana.objects.create(
                district=district,
                name=thana['thana'],
            )

        self.stdout.write(self.style.SUCCESS('Data populated successfully.'))