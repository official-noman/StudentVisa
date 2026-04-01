from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("visa", "0045_metakeywordpool_alter_seosettings_meta_description_and_more"),
    ]

    operations = [
        migrations.CreateModel(
            name="PageSEOSettings",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "site_name",
                    models.CharField(default="Student Visa BD", max_length=100),
                ),
                (
                    "page_key",
                    models.CharField(
                        choices=[
                            ("home", "Home"),
                            ("consultant_list", "Consultant List"),
                            (
                                "consaltant_wise_scholarship",
                                "Scholarship - Consultant Wise",
                            ),
                            (
                                "country_wise_scholarship",
                                "Scholarship - Country Wise",
                            ),
                            ("self_funded_programs", "Scholarship - Self Funded"),
                            ("scholarship_procedure_list", "Scholarship Procedure"),
                            ("offer_letter", "How To Apply - Offer Letter"),
                            ("by_country", "How To Apply - By Country"),
                            ("addresses", "Contact - Address"),
                            ("feedback-home", "Contact - Feedback"),
                            ("maps", "Contact - Location Map"),
                        ],
                        max_length=100,
                        unique=True,
                    ),
                ),
                (
                    "meta_title",
                    models.CharField(
                        blank=True,
                        help_text="Page-specific browser tab title",
                        max_length=60,
                    ),
                ),
                (
                    "meta_description",
                    models.TextField(
                        blank=True,
                        help_text="Page-specific SEO description",
                        max_length=150,
                    ),
                ),
                (
                    "meta_keywords",
                    models.TextField(blank=True, help_text="Comma separated keywords"),
                ),
                (
                    "og_image",
                    models.ImageField(
                        blank=True,
                        help_text="Page-specific social sharing image 1200x630",
                        null=True,
                        upload_to="seo/og/pages/",
                    ),
                ),
                (
                    "google_verification_id",
                    models.CharField(
                        blank=True,
                        help_text="Optional page-specific verification ID",
                        max_length=255,
                        null=True,
                    ),
                ),
                (
                    "analytics_code",
                    models.TextField(
                        blank=True,
                        help_text="Optional page-specific analytics override",
                        null=True,
                    ),
                ),
                (
                    "asset_version",
                    models.CharField(
                        blank=True,
                        default="",
                        help_text="Optional page-specific asset version",
                        max_length=10,
                    ),
                ),
                ("updated_at", models.DateTimeField(auto_now=True)),
            ],
            options={
                "verbose_name": "Page SEO Setting",
                "verbose_name_plural": "Page SEO Settings",
            },
        ),
    ]
