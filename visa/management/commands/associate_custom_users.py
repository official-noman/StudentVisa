from django.core.management.base import BaseCommand
from visa.models import CustomUser, Users, Students


class Command(BaseCommand):
    help = 'Copy data from Users and Students to CustomUser'

    def handle(self, *args, **options):
        # Copy data from Users
        users_instances = Users.objects.all()

        for user_instance in users_instances:
            try:
                # Explicitly set the id field
                custom_user_instance, created = CustomUser.objects.get_or_create(
                    id=user_instance.id,
                    email=user_instance.email,
                    defaults={
                        'password': user_instance.raw_password,
                        'username': user_instance.user_name,
                    }
                )

                if created:
                    self.stdout.write(self.style.SUCCESS(f"CustomUser created for {user_instance.full_name}."))
                else:
                    self.stdout.write(self.style.SUCCESS(f"CustomUser already exists for {user_instance.full_name}."))

                # Update the consultant_user field in Users
                user_instance.consultant_user = custom_user_instance
                user_instance.save()

            except Exception as e:
                self.stdout.write(self.style.ERROR(f"Error processing {user_instance.full_name}: {str(e)}"))

        # Copy data from Students
        students_instances = Students.objects.all()

        for student_instance in students_instances:
            try:
                # Explicitly set the id field
                custom_user_instance, created = CustomUser.objects.get_or_create(
                    id=student_instance.id,
                    email=student_instance.email,
                    defaults={
                        'password': student_instance.raw_password,
                        'username': student_instance.full_name,
                        # Add other fields as needed
                    }
                )

                if created:
                    self.stdout.write(self.style.SUCCESS(f"CustomUser created for {student_instance.full_name}."))
                else:
                    self.stdout.write(self.style.SUCCESS(f"CustomUser already exists for {student_instance.full_name}."))

                # Update the student_user field in Students
                student_instance.student_user = custom_user_instance
                student_instance.save()

            except Exception as e:
                self.stdout.write(self.style.ERROR(f"Error processing {student_instance.full_name}: {str(e)}"))
