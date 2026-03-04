from django.contrib.auth.hashers import make_password
from django.core.management.base import BaseCommand
from django.db import transaction
from visa.models import Users, Students, CustomUser

class Command(BaseCommand):
    help = 'Update phone field for student and consultant users'

    def handle(self, *args, **options):
        with transaction.atomic():
            # Update phones for students
            for student in Students.objects.all():
                if hasattr(student, 'student_user') and student.student_user:
                    student.student_user.phone = student.phone
                    student.student_user.save()

            # Update phones for consultants
            for consultant in Users.objects.all():
                if hasattr(consultant, 'consultant_user') and consultant.consultant_user:
                    consultant.consultant_user.phone = consultant.phone
                    consultant.consultant_user.save()

        self.stdout.write(self.style.SUCCESS('Successfully updated phone numbers for students and consultants.'))