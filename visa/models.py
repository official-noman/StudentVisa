# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has on_delete set to the desired behavior
#   * Remove managed = False lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone
from django.core.validators import MaxValueValidator, MinValueValidator
import os
from uuid import uuid4
from django.utils.text import slugify
import unicodedata
from django.conf import settings
from django.dispatch import receiver
from django.db.models.signals import post_save
from django_ckeditor_5.fields import CKEditor5Field


class CustomUser(AbstractUser):
    USER_TYPE_CHOICES = (
        (0, "Root"),
        (1, "Consultant"),
        (2, "Student"),
    )
    username = models.CharField(max_length=20, null=True, blank=True)
    user_type = models.IntegerField(choices=USER_TYPE_CHOICES, default=0)
    phone = models.CharField(max_length=125, blank=True, null=True)
    last_active = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.email

    db_table = "CustomUser"


class Addresses(models.Model):
    id = models.BigAutoField(primary_key=True)
    consultant_id = models.IntegerField(null=True)
    root_id = models.IntegerField(null=True)
    office_name = models.CharField(max_length=255)
    address = models.CharField(max_length=255)
    hotline = models.CharField(max_length=255)
    phone = models.CharField(max_length=255)
    email = models.CharField(max_length=255)
    created_at = models.DateTimeField(blank=True, null=True)
    updated_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        db_table = "addresses"


class Message(models.Model):
    CATEGORY_CHOICES = [
        ("General Inquiry", "General Inquiry"),
        ("Visa Application", "Visa Application"),
        ("Document Submission", "Document Submission"),
        ("Appointment Request", "Appointment Request"),
    ]

    category = models.CharField(max_length=255, choices=CATEGORY_CHOICES)
    email = models.EmailField()
    name = models.CharField(max_length=255)
    phonenumber = models.CharField(
        max_length=20
    )  # Assuming phone numbers are stored as strings
    subject = models.CharField(max_length=255)
    message = models.TextField()
    created_at = models.DateTimeField(blank=True, null=True)
    is_read = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.category} - {self.subject} - {self.name}"


class Notification(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    message = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.user.username} - {self.message}"


class Reply(models.Model):
    message = models.ForeignKey(Message, on_delete=models.CASCADE)
    email = models.EmailField()
    reply_text = models.TextField(null=True)
    created_at = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return f"Reply to: {self.message.subject} - {self.email}"


class Balances(models.Model):
    acc_paid_by = models.IntegerField(blank=True, null=True)
    acc_pay_to = models.IntegerField(blank=True, null=True)
    acc_pay_std_id = models.IntegerField(blank=True, null=True)
    pay_method = models.IntegerField(
        choices=[
            (1, "Cash"),
            (2, "Bank Deposit"),
            (3, "Check"),
        ],
        blank=True,
        null=True,
    )
    payment_status = models.IntegerField(
        choices=[
            (1, "Paid"),
            (2, "Checking"),
        ],
        blank=True,
        null=True,
    )
    acc_pay_ref = models.CharField(max_length=255, blank=True, null=True)
    acc_credit = models.FloatField(blank=True, null=True)
    acc_debit = models.FloatField(blank=True, null=True)
    acc_deal_type = models.IntegerField(blank=True, null=True)
    created_at = models.DateTimeField(blank=True, null=True)
    updated_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        db_table = "balances"


class Colors(models.Model):
    header_color = models.CharField(max_length=255)
    content_color = models.CharField(max_length=255)
    footer_color = models.CharField(max_length=255)
    consultant_id = models.IntegerField()
    created_at = models.DateTimeField(blank=True, null=True)
    updated_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        db_table = "colors"


class Countries(models.Model):
    country_id = models.AutoField(primary_key=True)
    country_name = models.CharField(max_length=30)
    country_code = models.CharField(max_length=10, blank=True, null=True)
    country_flag = models.CharField(max_length=60)
    country_howtoapply = models.TextField(
        db_column="country_howToApply"
    )  # Field name made lowercase.
    country_insertdate = models.DateField(
        db_column="country_insertDate", blank=True, null=True
    )  # Field name made lowercase.
    country_updatedate = models.DateField(
        db_column="country_updateDate", blank=True, null=True
    )  # Field name made lowercase.
    country_status = models.IntegerField(blank=True, null=True)

    class Meta:
        db_table = "countries"


class University(models.Model):
    university_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)
    abbreviation = models.CharField(max_length=50, blank=True, null=True)
    country = models.ForeignKey(
        Countries,
        on_delete=models.CASCADE,
        related_name="universities_new",
        null=True,
        blank=True,
    )
    state = models.CharField(max_length=100, blank=True, null=True)
    city = models.CharField(max_length=100, blank=True, null=True)
    university_logo = models.ImageField(upload_to="university_logos/", blank=True, null=True)
    website = models.URLField(max_length=200, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    status = models.IntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "universities"
        verbose_name = "University"
        verbose_name_plural = "Universities"

    def __str__(self):
        return f"{self.name} ({self.city}, {self.country.country_name})"


class UniversityWiseScholarship(models.Model):
    uws_id = models.AutoField(primary_key=True)
    university = models.ForeignKey(
        University,
        on_delete=models.CASCADE,
        related_name="scholarships"
    )
    title = models.CharField(max_length=500)
    image = models.ImageField(upload_to="university_scholarships/", blank=True, null=True)
    apply_procedure = CKEditor5Field("Apply Procedure", config_name="extends")
    visa_requirements = CKEditor5Field("Visa Requirements", config_name="extends")
    description = CKEditor5Field("Scholarship Description", config_name="extends")
    status = models.IntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "university_wise_scholarships"
        verbose_name = "University Wise Scholarship"
        verbose_name_plural = "University Wise Scholarships"

    def __str__(self):
        return f"{self.title} - {self.university.name}"


class ScholarshipStep(models.Model):
    country = models.ForeignKey(
        Countries,
        on_delete=models.CASCADE,
        related_name="scholarship_steps"
    )
    step_number = models.IntegerField()
    title = models.CharField(max_length=255)
    description = CKEditor5Field('Text', config_name='extends')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "scholarship_steps"
        ordering = ['step_number']

    def __str__(self):
        return f"{self.country.country_name} - Step {self.step_number}: {self.title}"


def image_upload_path(instance, filename):
    folder = "customizes_images"  # Example folder name
    original_name, ext = os.path.splitext(filename)
    try:
        consultant = Users.objects.filter(
            consultant_user_id=instance.consultant_id
        ).first()
        if consultant is None:
            consultant = Users.objects.get(id=instance.consultant_id)
        company_name = consultant.company_name
    except Users.DoesNotExist:
        # Handle case where consultant doesn't exist
        company_name = "unknown_company"
    new_filename = f"{instance.consultant_id}-{slugify(company_name)}-home{ext}"
    return os.path.join(folder, new_filename)


class Customizes(models.Model):
    description = models.TextField(blank=True, null=True)
    consultant = models.ForeignKey(
        CustomUser, on_delete=models.CASCADE, blank=True, null=True
    )
    image = models.ImageField(upload_to=image_upload_path, blank=True, null=True)
    status = models.IntegerField()
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(default=timezone.now)
    benefit = models.CharField(max_length=5000, blank=True, null=True)

    class Meta:
        db_table = "customizes"

    def save(self, *args, **kwargs):
        if self.image:
            # Constructing the new filename
            self.image.name = image_upload_path(self, self.image.name)
        super().save(*args, **kwargs)


class Explanation(models.Model):
    root_id = models.IntegerField()
    exp_title = models.CharField(max_length=500, blank=True, null=True)
    exp_des = models.TextField(null=True, blank=True)
    exp_img = models.ImageField(upload_to="explanation/", null=True, blank=True)
    created_at = models.DateTimeField(auto_now=True, blank=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, blank=True, null=True)


class Clients(models.Model):
    root_id = models.IntegerField()
    client_image = models.ImageField(upload_to="clients/", null=True, blank=True)
    client_name = models.CharField(max_length=100, blank=True, null=True)
    client_url = models.CharField(max_length=100, blank=True, null=True)
    created_at = models.DateTimeField(blank=True, null=True)
    updated_at = models.DateTimeField(blank=True, null=True)


class ConsultantDetails(models.Model):
    consultant_id = models.IntegerField()
    consultant_customizes = models.ManyToManyField(
        Customizes, related_name="consultant_customizes", null=True
    )
    consultant_img = models.ImageField(
        upload_to="consultant_images/", blank=True, null=True
    )
    experience = models.IntegerField(null=True, blank=True)
    consultant_maplocation = models.TextField(
        db_column="consultant_mapLocation", blank=True, null=True
    )
    consultant_requirement = models.TextField(blank=True, null=True)
    consultant_requirement_image = models.ImageField(
        upload_to="consultant_requirement/", blank=True, null=True
    )
    consultant_logo = models.ImageField(
        upload_to="consultant_logo/", blank=True, null=True
    )
    consultant_facebook = models.CharField(max_length=50, blank=True, null=True)
    consultant_website = models.CharField(max_length=150, blank=True, null=True)
    consultant_twitter = models.CharField(max_length=50, blank=True, null=True)
    consultant_googleplus = models.CharField(max_length=50, blank=True, null=True)
    consultant_youtube = models.CharField(max_length=150, blank=True, null=True)
    consultant_linkedin = models.CharField(max_length=150, blank=True, null=True)
    consultant_countries = models.ManyToManyField(
        Countries, related_name="consultant_details", null=True
    )
    status = models.IntegerField(default=0)
    consultant_experience = models.IntegerField(blank=True, null=True)
    consultant_designation = models.CharField(max_length=60, blank=True)
    consultant_bio = models.CharField(max_length=150, null=True, blank=True)
    consultant_intro = models.CharField(max_length=150, null=True, blank=True)
    consultant_description = models.CharField(max_length=1000, null=True, blank=True)
    created_at = models.DateTimeField(blank=True, null=True)
    updated_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        db_table = "consultant_details"
        managed = True

    def save(self, *args, **kwargs):
        if self.consultant_img:
            original_name = str(self.consultant_img)
            _, ext = os.path.splitext(original_name)

            try:
                # Fetch the consultant
                consultant = Users.objects.get(id=self.consultant_id)
                full_name = consultant.full_name
                company_name = consultant.company_name
            except Users.DoesNotExist:
                # Handle case where consultant doesn't exist
                full_name = "unknown_user"
                company_name = "unknown_company"

            # Constructing the new filename
            new_name = f"{self.consultant_id}-{slugify(company_name)}-{slugify(full_name)}{ext}"
            new_name = new_name.replace("_", "-")  # Replace underscores with hyphens
            self.consultant_img.name = new_name

        if self.consultant_requirement_image:
            original_name = str(self.consultant_img)
            _, ext = os.path.splitext(original_name)

            try:
                # Fetch the consultant
                consultant = Users.objects.get(id=self.consultant_id)
                full_name = consultant.full_name
                company_name = consultant.company_name
            except Users.DoesNotExist:
                # Handle case where consultant doesn't exist
                full_name = "unknown_user"
                company_name = "unknown_company"

            # Constructing the new filename
            new_name = f"{self.consultant_id}-{slugify(company_name)}-{slugify(full_name)}_Student-Visa-Bd{ext}"
            new_name = new_name.replace("_", "-")  # Replace underscores with hyphens
            self.consultant_requirement_image.name = new_name

        super().save(*args, **kwargs)


class ConsultantImages(models.Model):
    id = models.BigAutoField(primary_key=True)
    image = models.ImageField(upload_to="consultant_images/", blank=True, null=True)
    caption = models.CharField(max_length=255)
    consultant_id = models.IntegerField()
    created_at = models.DateTimeField(blank=True, null=True)
    updated_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        db_table = "consultant_images"

    def save(self, *args, **kwargs):
        if self.image:
            original_name = str(self.image)
            _, ext = os.path.splitext(original_name)

            # Fetch the consultant
            try:
                consultant = Users.objects.get(id=self.consultant_id)
                company_name = consultant.company_name
                print("Company Name:", company_name)  # Add this line to debug
            except Users.DoesNotExist:
                company_name = "unknown_company"  # Or handle this case accordingly

            # Constructing the new filename with the consultant's ID, company name, and original image name
            new_name = f"{self.consultant_id}-{company_name.replace(' ', '-').lower()}-{self.caption.replace(' ', '-')}{ext}"
            new_name = new_name.replace("_", "-")  # Replace underscores with hyphens
            print("New Name:", new_name)  # Add this line to debug
            self.image.name = new_name
        super().save(*args, **kwargs)

    def save(self, *args, **kwargs):
        if self.image:
            original_name = str(self.image)
            _, ext = os.path.splitext(original_name)

            try:
                # Fetch the consultant
                consultant = Users.objects.get(id=self.consultant_id)
                full_name = consultant.full_name
                company_name = consultant.company_name
            except Users.DoesNotExist:
                # Handle case where consultant doesn't exist
                full_name = "unknown_user"
                company_name = "unknown_company"

            # Constructing the new filename
            new_name = f"{self.consultant_id}-{slugify(company_name)}-{self.caption.replace(' ', '-')}{ext}"
            new_name = new_name.replace("_", "-")  # Replace underscores with hyphens
            self.image.name = new_name

        super().save(*args, **kwargs)


class ConsultantWises(models.Model):
    scow_id = models.AutoField(primary_key=True)
    scow_consultant_id = models.IntegerField(unique=True)
    scow_text = models.TextField()
    scow_whocanapply = models.TextField(
        db_column="scow_whoCanApply", blank=True, null=True
    )  # Field name made lowercase.
    scow_status = models.IntegerField()
    country_name = models.ForeignKey(
        Countries,
        on_delete=models.CASCADE,
        related_name="consultants",
        blank=True,
        null=True,
    )
    created_at = models.DateTimeField(blank=True, null=True)
    updated_at = models.DateTimeField(blank=True, null=True)
    expiration_time = models.DateTimeField(blank=True, null=True)

    class Meta:
        db_table = "consultant_wises"


class CountryAdds(models.Model):
    consultant_id = models.IntegerField()
    country_id = models.IntegerField()
    created_at = models.DateTimeField(blank=True, null=True)
    updated_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        db_table = "country_adds"


class CountryWises(models.Model):
    scw_id = models.AutoField(primary_key=True)
    scw_country_id = models.IntegerField(unique=True)
    scw_title = models.CharField(max_length=500, blank=True, null=True)
    scw_text = models.TextField()
    scw_whocanapply = models.TextField(
        db_column="scw_whoCanApply", blank=True, null=True
    )
    scw_status = models.IntegerField()
    scw_image = models.ImageField(
        upload_to="country_wise_scholarship_images/", blank=True, null=True
    )
    created_at = models.DateTimeField(blank=True, null=True)
    updated_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        db_table = "country_wises"


class FailedJobs(models.Model):
    id = models.PositiveBigIntegerField(primary_key=True)
    connection = models.TextField()
    queue = models.TextField()
    payload = models.TextField()
    exception = models.TextField()
    failed_at = models.DateTimeField()

    class Meta:
        db_table = "failed_jobs"


class Galleries(models.Model):
    image = models.CharField(max_length=255)
    caption = models.CharField(max_length=255)
    consultant_id = models.IntegerField()
    status = models.IntegerField()
    created_at = models.DateTimeField(blank=True, null=True)
    updated_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        db_table = "galleries"


class HomeFeedback(models.Model):
    # fdk_id = models.AutoField(primary_key=True)
    consultant = models.IntegerField()
    student = models.IntegerField(null=True, blank=True)
    subject = models.CharField(max_length=500, blank=True, null=True)
    fdk_fullname = models.CharField(
        db_column="fdk_fullName", max_length=30
    )  # Field name made lowercase.
    fdk_email = models.CharField(max_length=30)
    fdk_phone = models.CharField(max_length=15, blank=True, null=True)
    fdk_nameofcompany = models.CharField(
        db_column="fdk_nameOfCompany", max_length=30, blank=True, null=True
    )  # Field name made lowercase.
    fdk_website = models.CharField(max_length=20, blank=True, null=True)
    fdk_msg = models.TextField()
    fdk_status = models.IntegerField(default=1, null=True)
    country = models.CharField(max_length=40, blank=True, null=True)
    created_at = models.DateTimeField(blank=True, null=True)
    updated_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        db_table = "home_feedback"
        # engine = 'InnoDB'

    def __str__(self):
        return self.fdk_nameofcompany


class Review(models.Model):
    consultant = models.IntegerField()
    student = models.IntegerField()
    raw_rating = models.IntegerField()
    rating = models.FloatField(
        default=0, validators=[MinValueValidator(1), MinValueValidator(5)]
    )
    comment = models.TextField(null=True, blank=True, max_length=1000)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "review"

    def __str__(self):
        return str(self.rating)

    def save(self, *args, **kwargs):
        rating_check = Review.objects.filter(
            consultant=self.consultant, student=self.student
        ).first()
        super().save(*args, **kwargs)

        student_ratings = Review.objects.filter(
            consultant=self.consultant, student=self.student
        )
        new_student_rating = Review.objects.filter(
            consultant=self.consultant, student=self.student
        ).first()
        consultant = Users.objects.filter(id=self.consultant).first()
        student = Students.objects.filter(id=self.student).first()

        if consultant is not None and student is not None:
            if len(student_ratings) > 1:
                consultant.rating = self.rating
                print("student rating on model: ", student_ratings)

            else:
                if consultant.no_of_ratings == "" or consultant.no_of_ratings == None:
                    consultant.no_of_ratings = 0

                if consultant.rating == "" or consultant.rating == None:
                    consultant.rating = 0

                if (
                    consultant.no_of_ratings == 0
                    and consultant.rating == 0.0
                    and rating_check is None
                ):
                    consultant.rating = self.rating
                    consultant.no_of_ratings += 1

                # elif rating_check is not None:
                #     consultant.rating = self.rating

                else:
                    # total_rating = sum(review.raw_rating for review in reviews)
                    if rating_check is not None:
                        total_ratings = consultant.rating * consultant.no_of_ratings
                        student_new_rating = int(new_student_rating.rating)
                        new_total_ratings = (
                            total_ratings - rating_check.rating + student_new_rating
                        )

                        new_rating = round(
                            new_total_ratings / consultant.no_of_ratings, 1
                        )

                        consultant.rating = new_rating

                    else:
                        total_ratings = consultant.rating * consultant.no_of_ratings
                        new_total_ratings = total_ratings + self.rating

                        num_ratings = consultant.no_of_ratings + 1
                        new_rating = round(new_total_ratings / num_ratings, 1)
                        consultant.rating = new_rating
                        consultant.no_of_ratings += 1

            consultant.save()


class Levels(models.Model):
    balance_id = models.IntegerField(blank=True, null=True)
    student_id = models.IntegerField(blank=True, null=True)
    consultant_id = models.IntegerField(blank=True, null=True)
    level_1 = models.IntegerField(blank=True, unique=True, null=True)
    level_2 = models.IntegerField(blank=True, unique=True, null=True)
    level_3 = models.IntegerField(blank=True, unique=True, null=True)
    level_4 = models.IntegerField(blank=True, unique=True, null=True)
    level_5 = models.IntegerField(blank=True, unique=True, null=True)
    status = models.IntegerField(blank=True, null=True)
    created_at = models.DateTimeField(blank=True, null=True)
    updated_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        db_table = "levels"

    def save(self, *args, **kwargs):
        # Check if the student_id and consultant_id match in StudentDetails
        student_details = StudentDetails.objects.filter(
            dets_regs_id=self.student_id,
            dets_favconsultantlist__contains=str(self.consultant_id),
        )
        if student_details.exists():
            student_details = student_details.first()
            consultant_status, created = ConsultantStatus.objects.get_or_create(
                student=student_details, consultant_id=self.consultant_id
            )
            consultant_status.status = StudentDetails.VIEWED  # Set status to VIEWED (1)
            consultant_status.save()

        super().save(*args, **kwargs)


class Maps(models.Model):
    id = models.BigAutoField(primary_key=True)
    map_location = models.TextField(blank=True, null=True)
    consultant_id = models.IntegerField(blank=True, null=True)
    created_at = models.DateTimeField(blank=True, null=True)
    updated_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        db_table = "maps"


class Migrations(models.Model):
    id = models.PositiveIntegerField(primary_key=True)
    migration = models.CharField(max_length=255)
    batch = models.IntegerField()

    class Meta:
        db_table = "migrations"


class OfferLetters(models.Model):
    id = models.BigAutoField(primary_key=True)
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    status = models.IntegerField()
    created_at = models.DateTimeField(blank=True, null=True)
    updated_at = models.DateTimeField(blank=True, null=True)

    # Add the image field
    image = models.ImageField(upload_to="offer_letter_images/", blank=True, null=True)

    class Meta:
        db_table = "offer_letters"

    # def save(self, *args, **kwargs):
    #     # If the image field is not empty
    #     if self.image:
    #         original_name = str(self.image)
    #         _, ext = os.path.splitext(original_name)

    #         # Constructing the new filename with the ID and title
    #         new_name = f"{self.id}-{slugify(self.title)}{ext}"
    #         new_name = new_name.replace('_', '-')  # Replace underscores with hyphens
    #         self.image.name = new_name

    #     super().save(*args, **kwargs)


class PasswordResets(models.Model):
    email = models.CharField(max_length=255)
    token = models.CharField(max_length=255)
    created_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        db_table = "password_resets"


class Rates(models.Model):
    id = models.BigAutoField(primary_key=True)
    rate_added_by = models.IntegerField()
    rate_added_to = models.BigIntegerField()
    first_rate = models.FloatField(blank=True, null=True)
    second_rate = models.FloatField(blank=True, null=True)
    third_rate = models.FloatField(blank=True, null=True)
    four_rate = models.FloatField(blank=True, null=True)
    five_rate = models.FloatField(blank=True, null=True)
    created_at = models.DateTimeField(blank=True, null=True)
    updated_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        db_table = "rates"


def certificate_file_path(instance, filename, result_type):
    # Get the file extension
    ext = filename.split(".")[-1]
    # Get the full name of the student associated with this result
    student = Students.objects.get(id=instance.student_id)
    full_name = student.full_name.replace(" ", "-")  # Replace spaces with underscores
    # Construct the filename with the desired format
    filename = f"{instance.student_id}-{full_name}-{result_type}.{ext}"
    # Return the full file path
    return filename


class MastersDegree(models.Model):
    student_id = models.IntegerField()
    result = models.FloatField(blank=True, null=True)
    department = models.CharField(max_length=255, blank=True, null=True)
    university = models.CharField(max_length=255, blank=True, null=True)
    passing_year = models.IntegerField(blank=True, null=True)
    enrolled = models.BooleanField(default=False, blank=True, null=True)
    certificate_copy = models.ImageField(
        upload_to="certificates/", blank=True, null=True
    )
    verification_status = models.CharField(
        max_length=20,
        choices=[
            ("pending", "Pending"),
            ("verified", "Verified"),
            ("rejected", "Rejected"),
        ],
        default="pending",
    )
    rejection_note = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(blank=True, null=True)
    updated_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        db_table = "masters degree"


class CourseName(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name


class OtherCertification(models.Model):
    student_id = models.IntegerField()
    result = models.CharField(max_length=50, blank=True, null=True)
    course_name = models.ForeignKey(CourseName, on_delete=models.CASCADE)
    institute = models.CharField(max_length=255, blank=True, null=True)
    passing_year = models.IntegerField(blank=True, null=True)
    enrolled = models.BooleanField(default=False, blank=True, null=True)
    certificate_copy = models.ImageField(
        upload_to="certificates/", blank=True, null=True
    )
    verification_status = models.CharField(
        max_length=20,
        choices=[
            ("pending", "Pending"),
            ("verified", "Verified"),
            ("rejected", "Rejected"),
        ],
        default="pending",
    )
    rejection_note = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(blank=True, null=True)
    updated_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        db_table = "other_certification"


class Results(models.Model):
    id = models.BigAutoField(primary_key=True)
    secondary = models.IntegerField()
    secondary_board = models.CharField(max_length=100, blank=True, null=True)
    secondary_result = models.FloatField()
    secondary_roll_no = models.CharField(max_length=50, blank=True, null=True)
    secondary_reg_no = models.CharField(max_length=50, blank=True, null=True)
    secondary_certificate_no = models.CharField(max_length=255, blank=True, null=True)
    secondary_passing_year = models.IntegerField(blank=True, null=True)
    secondary_certificate_copy = models.ImageField(
        upload_to="certificates/", blank=True, null=True
    )
    secondary_verification_status = models.CharField(
        max_length=20,
        choices=[
            ("pending", "Pending"),
            ("verified", "Verified"),
            ("rejected", "Rejected"),
        ],
        default="pending",
    )

    higher = models.IntegerField(blank=True, null=True)
    higher_board = models.CharField(max_length=50, blank=True, null=True)
    higher_result = models.FloatField(blank=True, null=True)
    higher_roll_no = models.CharField(max_length=50, blank=True, null=True)
    higher_reg_no = models.CharField(max_length=50, blank=True, null=True)
    higher_certificate_no = models.CharField(max_length=255, blank=True, null=True)
    higher_passing_year = models.IntegerField(blank=True, null=True)
    higher_certificate_copy = models.ImageField(
        upload_to="certificates/", blank=True, null=True
    )
    higher_verification_status = models.CharField(
        max_length=20,
        choices=[
            ("pending", "Pending"),
            ("verified", "Verified"),
            ("rejected", "Rejected"),
        ],
        default="pending",
    )

    diploma = models.IntegerField(blank=True, null=True)
    diploma_board = models.CharField(max_length=50, blank=True, null=True)
    diploma_result = models.FloatField(blank=True, null=True)
    diploma_roll_no = models.CharField(max_length=50, blank=True, null=True)
    diploma_reg_no = models.CharField(max_length=50, blank=True, null=True)
    diploma_certificate_no = models.CharField(max_length=255, blank=True, null=True)
    diploma_passing_year = models.IntegerField(blank=True, null=True)
    diploma_certificate_copy = models.ImageField(
        upload_to="certificates/", blank=True, null=True
    )
    diploma_verification_status = models.CharField(
        max_length=20,
        choices=[
            ("pending", "Pending"),
            ("verified", "Verified"),
            ("rejected", "Rejected"),
        ],
        default="pending",
    )

    undergraduation = models.IntegerField(blank=True, null=True)
    university_name = models.CharField(max_length=300, blank=True, null=True)
    undergraduation_board = models.CharField(max_length=50, blank=True, null=True)
    undergraduation_result = models.FloatField(blank=True, null=True)
    undergraduation_passing_year = models.IntegerField(blank=True, null=True)
    undergraduation_certificate_copy = models.ImageField(
        upload_to="certificates/", blank=True, null=True
    )
    undergraduation_verification_status = models.CharField(
        max_length=20,
        choices=[
            ("pending", "Pending"),
            ("verified", "Verified"),
            ("rejected", "Rejected"),
        ],
        default="pending",
    )
    # other_courses = models.IntegerField(blank=True, null=True)

    phd = models.IntegerField(blank=True, null=True)
    phd_university = models.CharField(max_length=300, blank=True, null=True)
    phd_board = models.CharField(max_length=50, blank=True, null=True)
    phd_result = models.FloatField(blank=True, null=True)
    phd_passing_year = models.IntegerField(blank=True, null=True)
    phd_certificate_copy = models.ImageField(
        upload_to="certificates/", blank=True, null=True
    )
    phd_verification_status = models.CharField(
        max_length=20,
        choices=[
            ("pending", "Pending"),
            ("verified", "Verified"),
            ("rejected", "Rejected"),
        ],
        default="pending",
    )

    institution_name = models.CharField(max_length=300, blank=True, null=True)
    course_name = models.CharField(max_length=300, blank=True, null=True)
    course_result = models.CharField(max_length=300, blank=True, null=True)
    course_passing_year = models.IntegerField(blank=True, null=True)
    course_certificate_copy = models.ImageField(
        upload_to="certificates/", blank=True, null=True
    )
    secondary_rejection_note = models.TextField(blank=True, null=True)
    higher_rejection_note = models.TextField(blank=True, null=True)
    diploma_rejection_note = models.TextField(blank=True, null=True)
    undergraduation_rejection_note = models.TextField(blank=True, null=True)
    phd_rejection_note = models.TextField(blank=True, null=True)
    course_rejection_note = models.TextField(blank=True, null=True)
    student_id = models.IntegerField()
    created_at = models.DateTimeField(blank=True, null=True)
    updated_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        db_table = "results"

    # def save(self, *args, **kwargs):
    #     # Save the file paths before saving the model
    #     if self.secondary_certificate_copy:
    #         self.secondary_certificate_copy.name = certificate_file_path(self, self.secondary_certificate_copy.name, 'secondary')
    #     if self.higher_certificate_copy:
    #         self.higher_certificate_copy.name = certificate_file_path(self, self.higher_certificate_copy.name, 'higher')
    #     if self.undergraduation_certificate_copy:
    #         self.undergraduation_certificate_copy.name = certificate_file_path(self, self.undergraduation_certificate_copy.name, 'undergraduation')
    #     if self.course_certificate_copy:
    #         self.course_certificate_copy.name = certificate_file_path(self, self.course_certificate_copy.name, 'course')
    #     super().save(*args, **kwargs)

    # def get_student_full_name(self):
    #     student = Students.objects.get(id=self.student_id)
    #     return student.full_name

    # @property
    # def secondary_certificate_url(self):
    #     if self.secondary_certificate_copy:
    #         return f"{settings.MEDIA_URL}certificates/{self.secondary_certificate_copy.name}"
    #     return None

    # @property
    # def higher_certificate_url(self):
    #     if self.higher_certificate_copy:
    #         return f"{settings.MEDIA_URL}certificates/{self.higher_certificate_copy.name}"
    #     return None

    # @property
    # def undergraduation_certificate_url(self):
    #     if self.undergraduation_certificate_copy:
    #         return f"{settings.MEDIA_URL}certificates/{self.undergraduation_certificate_copy.name}"
    #     return None

    # @property
    # def course_certificate_url(self):
    #     if self.course_certificate_copy:
    #         return f"{settings.MEDIA_URL}certificates/{self.course_certificate_copy.name}"
    #     return None


class ScholarShips(models.Model):
    country_name = models.ForeignKey(
        Countries,
        on_delete=models.CASCADE,
        related_name="scholarships",
        blank=True,
        null=True,
    )
    schp_description = models.TextField(blank=True, null=True)
    apply_process = models.TextField(blank=True, null=True)
    consultant_id = models.IntegerField(blank=True, null=True)
    status = models.IntegerField(default=0)
    created_at = models.DateTimeField(blank=True, null=True)
    updated_at = models.DateTimeField(blank=True, null=True)
    expiration_time = models.DateTimeField(blank=True, null=True)

    class Meta:
        db_table = "scholar_ships"


# Define signal receiver function


# Define signal receiver function
@receiver(post_save, sender=ScholarShips)
def update_scholarship_status(sender, instance, **kwargs):
    # Check if expiration time has passed and status is still 1 (approved)
    if instance.expiration_time and instance.status == 1:
        # Convert expiration time to the same timezone as timezone.now()
        expiration_time = timezone.make_aware(
            instance.expiration_time, timezone.get_current_timezone()
        )
        if expiration_time < timezone.now():
            instance.status = 0  # Set status to 0
            instance.save()


class District(models.Model):
    # district_id = models.CharField(max_length=30, primary_key=True)
    name = models.CharField(max_length=30)
    lat = models.FloatField(blank=True, null=True)
    lon = models.FloatField(blank=True, null=True)
    website = models.CharField(max_length=100, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "district"


class Thana(models.Model):
    district = models.ForeignKey(
        District, on_delete=models.CASCADE, related_name="thanas"
    )
    name = models.CharField(max_length=30)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "thana"


class StudentDetails(models.Model):
    WAITING = 0
    VIEWED = 1

    STATUS_CHOICES = [
        (WAITING, "Waiting"),
        (VIEWED, "Viewed"),
    ]
    dets_id = models.AutoField(primary_key=True)
    dets_regs_id = models.IntegerField()
    dets_bloodgroup = models.CharField(
        db_column="dets_bloodGroup", max_length=5, blank=True, null=True
    )  # Field name made lowercase.
    dets_fathername = models.CharField(
        db_column="dets_fatherName", max_length=30, blank=True, null=True
    )  # Field name made lowercase.
    dets_mothername = models.CharField(
        db_column="dets_motherName", max_length=30, blank=True, null=True
    )  # Field name made lowercase.
    dets_nationality = models.CharField(max_length=15, blank=True, null=True)
    dets_dob = models.DateField(blank=True, null=True)
    student_image = models.ImageField(
        upload_to="student_images/", blank=True, null=True
    )
    dets_thumbnaillink = models.CharField(
        db_column="dets_thumbnailLink", max_length=60, blank=True, null=True
    )  # Field name made lowercase.
    dets_favconsultantlist = models.CharField(
        db_column="dets_favConsultantList", max_length=120, blank=True, null=True
    )  # Field name made lowercase.
    dets_updatedate = models.DateField(
        db_column="dets_updateDate", blank=True, null=True
    )  # Field name made lowercase.
    dets_status = models.IntegerField(default=0)

    class Meta:
        db_table = "student_details"


class ConsultantStatus(models.Model):
    student = models.ForeignKey("StudentDetails", on_delete=models.CASCADE)
    consultant_id = models.IntegerField()
    status = models.IntegerField(
        choices=StudentDetails.STATUS_CHOICES, default=StudentDetails.WAITING
    )


class Students(models.Model):
    full_name = models.CharField(max_length=30)
    student_user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, null=True)
    email = models.CharField(unique=True, max_length=30)
    phone = models.CharField(unique=True, max_length=125)
    otp = models.CharField(max_length=150, blank=True, null=True)
    USER_TYPE_CHOICES = [
        (0, "Student"),
        (1, "Guardian"),
    ]
    GENDER_CHOICES = [
        (0, "Male"),
        (1, "Female"),
    ]
    STATUS_CHOICE = [(0, "Inactive"), (1, "Acive"), (2, "Verified")]
    user_type = models.IntegerField(choices=USER_TYPE_CHOICES)
    gender = models.CharField(
        choices=GENDER_CHOICES, max_length=10, null=True, blank=True
    )
    dets_status = models.IntegerField(default=0)
    student_name = models.CharField(max_length=255, blank=True, null=True)
    relation = models.CharField(max_length=255, blank=True, null=True)
    district = models.ForeignKey(
        District, on_delete=models.SET_NULL, blank=True, null=True
    )
    thana = models.ForeignKey(Thana, on_delete=models.SET_NULL, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    country_id = models.CharField(max_length=150, blank=True, null=True)
    countries = models.ManyToManyField(
        Countries, blank=True, null=True, related_name="countries"
    )
    raw_password = models.CharField(max_length=60)
    password = models.CharField(max_length=255)
    status = models.IntegerField(choices=STATUS_CHOICE, default=0)
    created_at = models.DateTimeField(auto_now=True, blank=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, blank=True, null=True)

    class Meta:
        db_table = "students"
        managed = True


class UserSession(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()

    def __str__(self):
        return f"{self.user.username} - {self.start_time} to {self.end_time}"

    class Meta:
        verbose_name_plural = "User Sessions"


class Users(models.Model):
    full_name = models.CharField(max_length=30)
    consultant_user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, null=True)
    user_name = models.CharField(max_length=150, blank=True, null=True)
    email = models.CharField(unique=True, max_length=30)
    phone = models.CharField(unique=True, max_length=125)
    gender = models.CharField(max_length=50, blank=True, null=True)
    otp = models.CharField(max_length=150, blank=True, null=True)
    pin = models.CharField(max_length=50, blank=True, null=True)
    change_phone_otp = models.CharField(max_length=150, blank=True, null=True)
    about = models.TextField(blank=True, null=True)
    consultant_img = models.ImageField(
        upload_to="consultant_img/", blank=True, null=True
    )
    rating = models.FloatField(
        default=0.0,
        validators=[MinValueValidator(0.0), MinValueValidator(5.0)],
        null=True,
        blank=True,
    )
    no_of_ratings = models.IntegerField(default=0, null=True, blank=True)

    land_phone = models.CharField(max_length=20, blank=True, null=True)
    fax_no = models.CharField(max_length=20, blank=True, null=True)
    company_name = models.CharField(max_length=60, blank=True, null=True)
    est_date = models.DateField(blank=True, null=True)
    district = models.ForeignKey(
        District, on_delete=models.CASCADE, blank=True, null=True
    )
    thana = models.ForeignKey(Thana, on_delete=models.CASCADE, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    website = models.CharField(max_length=40, blank=True, null=True)
    raw_password = models.CharField(max_length=60)
    password = models.CharField(max_length=255)
    user_role = models.IntegerField(blank=True, null=True)

    active_status = models.IntegerField(blank=True, null=True)
    suspension_time = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(blank=True, null=True)
    updated_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        db_table = "users"
        managed = True

    def save(self, *args, **kwargs):
        if self.consultant_img:
            original_name = str(self.consultant_img)
            _, ext = os.path.splitext(original_name)
            new_name = (
                f"{self.id}-{slugify(self.full_name)}-{slugify(self.company_name)}{ext}"
            )
            new_name = new_name.replace("_", "-")
            self.consultant_img.name = new_name

        super().save(*args, **kwargs)


class TopConsultant(models.Model):
    consultant = models.OneToOneField(
        Users, 
        on_delete=models.CASCADE, 
        related_name="top_featured",
        db_constraint=False
    )
    order = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['order', '-created_at']

    def __str__(self):
        return self.consultant.full_name


# class StudentViewLog(models.Model):
#     consultant_id =models.CharField(max_length=20, blank=True, null=True)
#     student_id = models.CharField(max_length=20, blank=True, null=True)
#     lead_level = models.IntegerField()  # Lead level clicked (0 for "My Lead", 1-5 for other leads)
#     viewed_at = models.DateTimeField(auto_now_add=True)

#     class Meta:
#         db_table = 'student_view_log'
#         managed = True


from django_ckeditor_5.fields import CKEditor5Field


class VisaService(models.Model):
    title = models.CharField(max_length=200)
    subtitle = models.CharField(
        max_length=255, help_text="Short detail like 'Subclass 500'"
    )
    slug = models.SlugField(unique=True, blank=True)
    image = models.ImageField(upload_to="services/")
    short_description = models.TextField()
    content = CKEditor5Field("Content", config_name="extends")  # মেইন ডিটেইলস পেজের জন্য
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title
    
    # models.py

class OTPRequest(models.Model):
    phone_number = models.CharField(max_length=15)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"OTP request for {self.phone_number} at {self.timestamp}"

class SelfFundedProgram(models.Model):
    university = models.ForeignKey(
        University,
        on_delete=models.CASCADE,
        related_name='self_funded_programs'
    )
    country = models.ForeignKey(
        'Countries',
        on_delete=models.PROTECT,
        related_name='self_funded_programs'
    )
    semester_fee = models.CharField(max_length=100)
    requirements = CKEditor5Field(config_name='extends')
    foreign_student_policy = CKEditor5Field(config_name='extends')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Self Funded Program'
        verbose_name_plural = 'Self Funded Programs'

    def __str__(self):
        return f"{self.university.name} — {self.country} (Fee: {self.semester_fee})"
class MetaKeywordPool(models.Model):
    word = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.word


class SEOSettings(models.Model):
    site_name = models.CharField(max_length=100, default="Student Visa BD")
    meta_title = models.CharField(
        max_length=60,
        help_text="Default browser tab title",
    )
    meta_description = models.TextField(
        max_length=150,
        help_text="SEO description for search engines",
    )
    meta_keywords = models.TextField(
        help_text="Comma separated keywords",
    )
    og_image = models.ImageField(
        upload_to="seo/og/",
        null=True,
        blank=True,
        help_text="Social media sharing image 1200x630",
    )
    google_verification_id = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        help_text="Google Search Console ID",
    )
    analytics_code = models.TextField(
        null=True,
        blank=True,
        help_text="Google Analytics or Facebook Pixel script",
    )
    asset_version = models.CharField(
        max_length=10,
        default="1.0",
        help_text="Version for CSS/JS cache busting (e.g. ?v=1.0)",
    )
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        # Preserve keyword normalization and also force a unique OG image path
        # for newly uploaded files so social preview caches do not reuse an old image URL.
        if self.meta_keywords:
            normalized_keywords = [
                keyword.strip().lower()
                for keyword in self.meta_keywords.split(",")
                if keyword.strip()
            ]
            self.meta_keywords = ", ".join(dict.fromkeys(normalized_keywords))

        if self.og_image and not getattr(self.og_image, "_committed", True):
            _, ext = os.path.splitext(self.og_image.name)
            ext = ext or ".jpg"
            self.og_image.name = f"seo/og/{uuid4().hex}{ext.lower()}"

        super().save(*args, **kwargs)


class PageSEOSettings(models.Model):
    PAGE_CHOICES = (
        ("home", "Home"),
        ("consultant_list", "Consultant List"),
        ("consaltant_wise_scholarship", "Scholarship - Consultant Wise"),
        ("country_wise_scholarship", "Scholarship - Country Wise"),
        ("self_funded_programs", "Scholarship - Self Funded"),
        ("scholarship_procedure_list", "Scholarship Procedure"),
        ("offer_letter", "How To Apply - Offer Letter"),
        ("by_country", "How To Apply - By Country"),
        ("addresses", "Contact - Address"),
        ("feedback-home", "Contact - Feedback"),
        ("maps", "Contact - Location Map"),
    )

    site_name = models.CharField(max_length=100, default="Student Visa BD")
    page_key = models.CharField(max_length=100, choices=PAGE_CHOICES, unique=True)
    meta_title = models.CharField(
        max_length=60,
        blank=True,
        help_text="Page-specific browser tab title",
    )
    meta_description = models.TextField(
        max_length=150,
        blank=True,
        help_text="Page-specific SEO description",
    )
    meta_keywords = models.TextField(
        blank=True,
        help_text="Comma separated keywords",
    )
    og_image = models.ImageField(
        upload_to="seo/og/pages/",
        null=True,
        blank=True,
        help_text="Page-specific social sharing image 1200x630",
    )
    google_verification_id = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        help_text="Optional page-specific verification ID",
    )
    analytics_code = models.TextField(
        null=True,
        blank=True,
        help_text="Optional page-specific analytics override",
    )
    asset_version = models.CharField(
        max_length=10,
        blank=True,
        default="",
        help_text="Optional page-specific asset version",
    )
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Page SEO Setting"
        verbose_name_plural = "Page SEO Settings"

    def __str__(self):
        return self.get_page_key_display()

    def save(self, *args, **kwargs):
        # Preserve keyword normalization and also force a unique OG image path
        # for newly uploaded files so page-specific social previews get a fresh image URL.
        if self.meta_keywords:
            normalized_keywords = [
                keyword.strip().lower()
                for keyword in self.meta_keywords.split(",")
                if keyword.strip()
            ]
            self.meta_keywords = ", ".join(dict.fromkeys(normalized_keywords))

        if self.og_image and not getattr(self.og_image, "_committed", True):
            _, ext = os.path.splitext(self.og_image.name)
            ext = ext or ".jpg"
            self.og_image.name = f"seo/og/pages/{uuid4().hex}{ext.lower()}"

        super().save(*args, **kwargs)
