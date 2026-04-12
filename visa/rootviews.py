from django.shortcuts import render, redirect
from .models import *
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.views.decorators.csrf import csrf_exempt
from django.core.serializers import serialize
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password
from django.views.decorators.http import require_POST
from django.db.models import Q
from django.db import transaction
from django.db.models import Sum
import os
from django.utils import timezone
from django.utils.text import slugify
from datetime import datetime
from django.db import IntegrityError
from django.db.models import Count
from datetime import timedelta
from django.db.models.functions import ExtractMonth
from django.db.models import Sum, F, Value
from django.db.models.functions import Coalesce
from django.db.models import Count, Max
from django.db.models.functions import ExtractMonth, ExtractYear, ExtractWeek
from django.http import HttpResponseRedirect
from django.http import JsonResponse
import json
from django.http import HttpResponse, JsonResponse, HttpResponseNotFound
from django.contrib.auth.hashers import check_password
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
from django.core.mail import send_mail
from django.conf import settings
from django.urls import reverse
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.decorators import permission_required
from functools import wraps
from django.contrib.auth.decorators import permission_required
from django.core.exceptions import PermissionDenied
from .decorators import root_required
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import University, Countries
# from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
# from django.http import JsonResponse
# from django.contrib import messages

# ---------------------------------------------------------------------------
# Import your models — adjust the import path to match your project structure
# ---------------------------------------------------------------------------
from .models import Countries, University, SelfFundedProgram


def role_and_permission_required(permission):
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            # Get the ID of the user from the request
            user_id = request.user.id

            # Check if the user is authenticated and has the specified role
            try:
                user = Users.objects.get(id=user_id)
                if user.user_role == 2:
                    # If the user has the required role, apply the permission_required decorator
                    return permission_required(permission, raise_exception=True)(
                        view_func
                    )(request, *args, **kwargs)
                else:
                    # If the user does not have the required role, raise PermissionDenied
                    raise PermissionDenied()
            except Users.DoesNotExist:
                # If the user does not exist, raise PermissionDenied
                raise PermissionDenied()

        return _wrapped_view

    return decorator


@login_required
@root_required
def root_home(request):
    # Count the total number of students, consultants, countries, and universities
    total_students = Students.objects.count()

    # Count consultants where user_role is 6
    total_consultants = Users.objects.filter(user_role=5).count()

    total_countries = Countries.objects.count()
    total_universities = University.objects.count()
    total_credit = (
        Balances.objects.filter(acc_credit__isnull=False).aggregate(
            total_credit=Sum("acc_credit")
        )["total_credit"]
        or 0
    )

    # Calculate total debit amount
    total_debit = (
        Balances.objects.filter(acc_debit__isnull=False).aggregate(
            total_debit=Sum("acc_debit")
        )["total_debit"]
        or 0
    )

    # Calculate total balance
    total_balance = total_credit - total_debit
    # Get the current year
    current_year = timezone.now().year

    # Calculate rate percentage for students in the current year
    students_by_year = Students.objects.filter(created_at__year=current_year).count()
    student_rates = calculate_rate_percentage(current_year, Students, students_by_year)

    # Calculate rate percentage for consultants in the current year
    consultants_by_year = Users.objects.filter(
        user_role=5, created_at__year=current_year
    ).count()
    consultant_rates = calculate_rate_percentage(
        current_year, Users, consultants_by_year
    )
    avg_time_on_site = calculate_avg_time_on_site(request.user.id)
    messages = Message.objects.all()
    unread_messages = messages.filter(is_read=False)
    unread_count = unread_messages.count()
    user_notifications = Notification.objects.filter(user=request.user, is_read=False)
    user_notifications.update(is_read=True)

    context = {
        "total_students": total_students,
        "total_consultants": total_consultants,
        "total_countries": total_countries,
        "total_universities": total_universities,
        "student_rates": student_rates,
        "consultant_rates": consultant_rates,
        "avg_time_on_site": avg_time_on_site,
        "messages": messages,
        "unread_count": unread_count,
        "notifications": user_notifications,
        "total_balance": total_balance,
    }

    return render(request, "roottemplates/index.html", context)


def export_dashboard_data(request):
    if request.method == "POST":
        # Count the total number of students, consultants, countries, and universities
        total_students = Students.objects.count()
        total_consultants = Users.objects.filter(user_role=5).count()
        total_countries = Countries.objects.count()
        total_universities = University.objects.count()

        # Calculate total credit and debit amounts
        total_credit = (
            Balances.objects.filter(acc_credit__isnull=False).aggregate(
                total_credit=Sum("acc_credit")
            )["total_credit"]
            or 0
        )
        total_debit = (
            Balances.objects.filter(acc_debit__isnull=False).aggregate(
                total_debit=Sum("acc_debit")
            )["total_debit"]
            or 0
        )

        # Calculate total balance
        total_balance = total_credit - total_debit

        # Get the current year
        current_year = timezone.now().year

        # Calculate rate percentage for students and consultants in the current year
        students_by_year = Students.objects.filter(
            created_at__year=current_year
        ).count()
        student_rates = calculate_rate_percentage(
            current_year, Students, students_by_year
        )
        consultants_by_year = Users.objects.filter(
            user_role=5, created_at__year=current_year
        ).count()
        consultant_rates = calculate_rate_percentage(
            current_year, Users, consultants_by_year
        )

        # Calculate average time on site
        avg_time_on_site = calculate_avg_time_on_site(request.user.id)

        # Get unread messages count and notifications
        messages = Message.objects.all()
        unread_messages = messages.filter(is_read=False)
        unread_count = unread_messages.count()
        user_notifications = Notification.objects.filter(
            user=request.user, is_read=False
        )
        user_notifications.update(is_read=True)

        # Prepare the data to be exported
        export_data = {
            "total_students": total_students,
            "total_consultants": total_consultants,
            "total_countries": total_countries,
            "total_universities": total_universities,
            "total_credit": total_credit,
            "total_debit": total_debit,
            "total_balance": total_balance,
            "student_rates": student_rates,
            "consultant_rates": consultant_rates,
            "avg_time_on_site": avg_time_on_site,
            "unread_count": unread_count,
            # Add more data as needed
        }

        # Return the data as a JSON response
        return JsonResponse(export_data)
    else:
        # If the request method is not POST, return an error response
        return JsonResponse(
            {"error": "Invalid request method. Must be POST."}, status=400
        )


@login_required
@root_required
def root_profile(request):
    if request.user.is_authenticated:
        print("user: ", request.user.email)
        user_id = request.user.id
        user = Users.objects.get(id=user_id)
        print("est. date: ", user.est_date)
        context = {
            "user": user,
        }
    return render(request, "roottemplates/root_profile.html", context)


def save_root_profile(request, user_id):
    if request.method == "POST" and request.user.is_authenticated:
        user = request.user
        if user.id == int(user_id):
            full_name = request.POST.get("full_name")

            website = request.POST.get("website")
            about = request.POST.get("about")
            old_password = request.POST.get("old_password")
            new_password = request.POST.get("new_password")
            confirm_password = request.POST.get("confirm_password")
            consultant_img = request.FILES.get("consultant_img")

            print("website: ", website)
            print("about: ", about)
            print("consultant_img: ", consultant_img)
            root_id = int(user_id)
            root = Users.objects.get(id=root_id)

            if website and about:
                root.full_name = full_name

                root.website = website
                root.about = about

                if consultant_img:
                    root.consultant_img = consultant_img

                if old_password and new_password and confirm_password:
                    if new_password == confirm_password:
                        if check_password(new_password, user.password):
                            user.set_password(new_password)
                        else:
                            return JsonResponse({"error": "Wrong old password"})
                    else:
                        return JsonResponse({"error": "Passwords do not match"})
                user.save()
                root.save()
                return JsonResponse({"success": True})
            else:
                return JsonResponse({"error": "Please fill up all the required fields"})
        else:
            return JsonResponse(
                {
                    "error": "Cannot update your account information due to security reasons"
                }
            )
    else:
        return JsonResponse({"error": "Invalid request"})


def calculate_rate_percentage(year, model, count):
    # Get the count for the previous year
    prev_year_count = model.objects.filter(created_at__year=year - 1).count()

    # Calculate rate percentage for the current year
    rate = 0.0
    increase_decrease = "No Change"

    if prev_year_count != 0:
        rate = ((count - prev_year_count) / prev_year_count) * 100

        if rate > 0:
            increase_decrease = "Increased"
        elif rate < 0:
            increase_decrease = "Decreased"

    return {"year": year, "rate": rate, "increase_decrease": increase_decrease}


def calculate_avg_time_on_site(user):
    # Calculate average time on site for the current user
    user_sessions = UserSession.objects.filter(user=user)

    if user_sessions.exists():
        total_duration = sum(
            (session.end_time - session.start_time).total_seconds()
            for session in user_sessions
        )
        avg_duration = total_duration / user_sessions.count()
        avg_time_on_site = str(timedelta(seconds=avg_duration))
        return avg_time_on_site
    else:
        return "0"


def monthly_balance_chart(request):
    # Assuming 'created_at' is the date field in your Balances model
    monthly_data = (
        Balances.objects.annotate(month=ExtractMonth("created_at"))
        .values("month")
        .annotate(credit=Sum("acc_credit"), debit=Sum("acc_debit"))
        .order_by("month")
    )

    labels = [get_month_name(month["month"]) for month in monthly_data]
    credit_data = [month["credit"] for month in monthly_data]
    debit_data = [month["debit"] for month in monthly_data]

    context = {
        "labels": labels,
        "credit_data": credit_data,
        "debit_data": debit_data,
    }

    return JsonResponse(context, safe=False)


def get_month_name(month_number):
    # Replace this with your own method to get month names
    return [
        "JAN",
        "FEB",
        "MAR",
        "APR",
        "MAY",
        "JUN",
        "JUL",
        "AUG",
        "SEP",
        "OCT",
        "NOV",
        "DEC",
    ][month_number - 1]


from django.db.models import Sum, ExpressionWrapper, F, FloatField, Case, When, Value


def type_of_balance(request):
    # Assuming you have a field named 'pay_method' in your Balances model
    totals = (
        Balances.objects.values("pay_method")
        .annotate(total_amount=Coalesce(Sum("acc_credit"), 0.0))
        .order_by("pay_method")
    )

    # Convert the queryset to a list of dictionaries
    totals_list = list(totals)

    # Create a dictionary to hold the result
    result = {"payment_method_totals": totals_list}

    # Return the result in JSON format
    return JsonResponse(result)


def root_consultant_list_json(request):
    approved_consultant_accounts = CustomUser.objects.filter(user_type=1)

    # Pending consultants are stored in Users. We should not exclude by raw id,
    # because Users.id and CustomUser.id are different auto-increment sequences
    # until an approval flow explicitly links them.
    root_consultants = (
        Users.objects.filter(user_role=5)
        .filter(Q(active_status__isnull=True) | Q(active_status=0))
        .exclude(
            email__in=approved_consultant_accounts.exclude(email__isnull=True).values(
                "email"
            )
        )
        .exclude(
            phone__in=approved_consultant_accounts.exclude(phone__isnull=True).values(
                "phone"
            )
        )
        .order_by("company_name")
    )

    # Extract specific fields from the queryset including 'phone' and 'id'
    root_consultants_data = root_consultants.values(
        "id", "full_name", "email", "company_name", "phone", "active_status"
    )

    # Convert the queryset data to a list
    root_consultants_list = list(root_consultants_data)

    # Calculate the total count
    total_count = root_consultants.count()

    # Return the JSON response with total count
    return JsonResponse(
        {"root_consultants": root_consultants_list, "total_count": total_count},
        safe=False,
    )


def count_consultant_perform(request):
    try:
        # Count occurrences of each consultant_id and get the last created_at
        consultant_counts = (
            Levels.objects.filter(status=1)
            .values("consultant_id")
            .annotate(count=Count("consultant_id"), last_activity=Max("created_at"))
        )

        # Return the result as JSON response
        return JsonResponse({"consultant_counts": list(consultant_counts)})
    except Exception as e:
        # Handle exceptions
        return JsonResponse({"error": str(e)}, status=500)


def count_students_monthly_entry(request):
    try:
        # Count occurrences of students entered each month
        students_counts = (
            Students.objects.annotate(
                month=ExtractMonth("created_at"),
            )
            .values("month")
            .annotate(count=Count("id"))
        )

        # Return the result as JSON response
        return JsonResponse({"students_counts": list(students_counts)})
    except Exception as e:
        # Handle exceptions
        return JsonResponse({"error": str(e)}, status=500)


def count_students_yearly_entry(request):
    try:
        # Count occurrences of students entered each year
        students_counts = (
            Students.objects.annotate(
                year=ExtractYear("created_at"),
            )
            .values("year")
            .annotate(count=Count("id"))
        )

        # Return the result as JSON response
        return JsonResponse({"students_counts": list(students_counts)})
    except Exception as e:
        # Handle exceptions
        return JsonResponse({"error": str(e)}, status=500)


def count_students_weekly_entry(request):
    try:
        # Count occurrences of students entered each week
        students_counts = (
            Students.objects.annotate(
                week=ExtractWeek("created_at"),
            )
            .values("week")
            .annotate(count=Count("id"))
        )

        # Return the result as JSON response
        return JsonResponse({"students_counts": list(students_counts)})
    except Exception as e:
        # Handle exceptions
        return JsonResponse({"error": str(e)}, status=500)


@permission_required("visa.view_message", raise_exception=True)
@login_required
@root_required
def message_list(request):
    # Get the search query from the request
    query = request.GET.get("q")

    # Retrieve all messages
    messages = Message.objects.order_by("-created_at")

    # If a search query is provided, filter messages based on the query
    if query:
        messages = messages.filter(
            Q(subject__icontains=query) | Q(text__icontains=query)
        )

    # Retrieve details of the currently logged-in user
    user_details = get_object_or_404(Users, id=request.user.id)

    # Pass the messages and the currently logged-in user details to the template
    context = {"messages": messages, "user_details": user_details}

    # Render the template with the context
    return render(request, "roottemplates/message_list.html", context)


@permission_required("visa.add_reply", raise_exception=True)
@login_required
def create_reply(request, message_id):
    if request.method == "POST":
        reply_text = request.POST.get("reply_text")

        try:
            message = Message.objects.get(pk=message_id)

            reply = Reply.objects.create(
                message=message,
                email=settings.EMAIL_HOST_USER,  # Replace with appropriate email address
                reply_text=reply_text,
                created_at=timezone.now(),
            )

            # Send email notification
            subject = f"Re: {message.subject}"
            body = f"Your message:\n{message.message}\n\nReply:\n{reply_text}"
            sender_email = settings.EMAIL_HOST_USER
            recipient_email = message.email

            try:
                send_mail(
                    subject, body, sender_email, [recipient_email], fail_silently=False
                )
            except Exception as e:
                # Handle email sending error (log, notify user, etc.)
                return JsonResponse({"error": "Failed to send email notification."})

            return JsonResponse(
                {"status": "success", "reply_id": reply.id}
            )  # Return reply ID

        except Message.DoesNotExist:
            return JsonResponse({"error": "Message not found."})

    else:
        return JsonResponse({"error": "Method Not Allowed."})


@csrf_exempt
def get_chat_history(request, message_id):
    message = get_object_or_404(Message, id=message_id)
    replies = message.reply_set.all().order_by("created_at")
    data = {
        "message": {
            "subject": message.subject,
            "message": message.message,
            "created_at": message.created_at,
        },
        "replies": [
            {
                "text": reply.reply_text,
                "email": reply.email,
                "created_at": reply.created_at,
            }
            for reply in replies
        ],
    }
    return JsonResponse(data)


@login_required
@root_required
def root_customize(request):
    # Check if there is an existing Customize instance
    user = request.user
    instance = Customizes.objects.filter(consultant=user).last()

    if user.is_authenticated:
        if request.method == "POST":
            user_id = request.user.id
            description = request.POST.get("description")
            status = request.POST.get("status", 1)
            image = request.FILES.get("image")

            if instance:
                instance.description = description
                instance.status = status

                # Check if a new image is provided
                if image:
                    # Delete the old static file
                    if instance.image:
                        old_image_path = os.path.join(
                            settings.MEDIA_ROOT, instance.image.name
                        )
                        if os.path.exists(old_image_path):
                            os.remove(old_image_path)
                    instance.image = image

                instance.updated_at = timezone.now()
                operation_type = "updated"

            else:
                instance = Customizes(
                    consultant=user,
                    description=description,
                    status=1,
                    created_at=timezone.now(),
                    updated_at=timezone.now(),
                )

                if image:
                    instance.image = image
                operation_type = "created"

            instance.save()

            messages.success(request, f"Customization {operation_type} successfully.")

    else:
        messages.error(request, f"Not Authorized to change content.")

    return render(request, "roottemplates/customize.html", {"instance": instance})


@login_required
@root_required
def offer_letters(request):
    # Check if there is an existing OfferLetters instance
    instance = OfferLetters.objects.first()

    if request.method == "POST":
        title = request.POST.get("title")
        description = request.POST.get("description")
        status = 1  # Set the status to 1

        # Handle the image field
        image = request.FILES.get("image")

        if instance:  # Update operation
            instance.title = title
            instance.description = description
            instance.status = status
            if image:
                instance.image = image
            instance.updated_at = timezone.now()
            operation_type = "updated"
        else:  # Create operation
            instance = OfferLetters(
                title=title,
                description=description,
                status=status,
                created_at=timezone.now(),
            )
            if image:
                instance.image = image
            operation_type = "created"

        instance.save()

        messages.success(request, f"Offer letter {operation_type} successfully.")

    return render(request, "roottemplates/offer_latter.html", {"instance": instance})


@login_required
@root_required
@require_POST
def delete_offer_letter(request, item_id):
    item = get_object_or_404(OfferLetters, pk=item_id)
    item.delete()
    messages.success(request, "Offer letter deleted successfully.")
    return redirect("offer_letters")


@login_required
@root_required
def root_countries(request):
    # Fetch the list of countries
    country_list = Countries.objects.all()

    return render(
        request, "roottemplates/countries.html", {"country_list": country_list}
    )


@login_required
def delete_country(request, country_id):
    country_list = Countries.objects.all()

    if request.method == "POST":
        country = get_object_or_404(Countries, pk=country_id)
        country.delete()
        return JsonResponse(
            {"success": True, "message": "Country deleted successfully!"}
        )

    country_list_json = serialize(
        "json",
        country_list,
        fields=("country_id", "country_name", "country_flag", "country_howtoapply"),
    )
    return JsonResponse({"country_list": country_list_json}, safe=False)


@login_required
@root_required
@csrf_exempt
def edit_country(request, country_id):
    # Fetch the country to be edited
    country = get_object_or_404(Countries, pk=country_id)

    if request.method == "POST":
        # Handle the edit operation
        # country_name = request.POST.get('country_name')
        # country_flag = request.POST.get('country_flag')
        country_howtoapply = request.POST.get("country_howtoapply")
        # country.country_name = country_name
        # country.country_flag = country_flag
        country.country_howtoapply = country_howtoapply
        country.save()

        messages.success(request, "Country Details updated successfully!")
        return redirect(
            "root_countries"
        )  # Replace 'your_redirect_view_name' with the actual view name

    return render(request, "roottemplates/edit_country.html", {"country": country})


@login_required
@root_required
@permission_required(
    ("visa.add_scholarships", "visa.change_scholarships"), raise_exception=True
)
def consultant_wise_scholarship(request):
    consultants = Users.objects.filter(user_role=5)
    countries = Countries.objects.all()

    if request.method == "POST":
        scow_text = request.POST.get("scow_text")
        scow_whocanapply = request.POST.get("scow_whocanapply")
        scow_status = request.POST.get("scow_status")
        consultant_id = request.POST.get("consultant_id")
        country_id = request.POST.get(
            "country_id"
        )  # Get the selected country ID from the form

        consultant_instance = Users.objects.get(id=consultant_id)
        country_instance = Countries.objects.get(country_id=country_id)
        expire_time_str = request.POST.get(
            "expiration_time"
        )  # Get the selected expiration time from the form as a string

        # Convert the string to a datetime object
        expire_time = (
            datetime.strptime(expire_time_str, "%Y-%m-%d") if expire_time_str else None
        )  # Retrieve the country instance

        try:
            instance = ConsultantWises.objects.create(
                scow_text=scow_text,
                scow_whocanapply=scow_whocanapply,
                scow_status=1,
                expiration_time=expire_time,
                scow_consultant_id=consultant_instance.id,
                country_name=country_instance,  # Save the selected country instance
                created_at=timezone.now(),
                updated_at=timezone.now(),
            )

            if not scow_status:
                instance.scow_status = 1
            operation_type = "created"

            messages.success(
                request, f"Consultant Wise Scholarship {operation_type} successfully."
            )
        except ValidationError as e:
            errors = e.message_dict
            for field, error_list in errors.items():
                for error in error_list:
                    messages.error(request, f"{field}: {error}")
        except Exception as e:
            messages.error(request, f"An error occurred: {e}")

    instances = ConsultantWises.objects.all()

    return render(
        request,
        "roottemplates/consultant_wise_scholarship.html",
        {"instances": instances, "consultants": consultants, "countries": countries},
    )


# def consultant_wise_scholarship(request):
#     # Fetch all users with user_type=1
#     consultants = Users.objects.filter(user_role=5)

#     if request.method == 'POST':
#         scow_text = request.POST.get('scow_text')
#         scow_whocanapply = request.POST.get('scow_whocanapply')
#         scow_status = request.POST.get('scow_status')
#         consultant_id = request.POST.get('consultant_id')

#         consultant_instance = Users.objects.get(id=consultant_id)

#         # Create a new instance without checking for an existing one
#         instance = ConsultantWises(
#             scow_text=scow_text,
#             scow_whocanapply=scow_whocanapply,
#             scow_status=scow_status,
#             scow_consultant_id=consultant_instance.id,
#             created_at=timezone.now(),
#             updated_at=timezone.now()
#         )
#         if not scow_status:
#             instance.scow_status = 1
#         operation_type = "created"

#         instance.save()

#         messages.success(request, f"Consultant Wise Scholarship {operation_type} successfully.")

#     # Fetch all instances of ConsultantWises
#     instances = ConsultantWises.objects.all()

#     return render(request, 'roottemplates/consultant_wise_scholarship.html', {'instances': instances, 'consultants': consultants})


@login_required
@root_required
@permission_required(
    "visa.add_scholarships", "visa.change_scholarships", raise_exception=True
)
def country_wise_scholarship_list(request):
    scholarships = CountryWises.objects.all()

    # Fetch related country information for each scholarship
    scholarship_data = []
    for scholarship in scholarships:
        country = Countries.objects.filter(country_id=scholarship.scw_country_id).first()
        if country:
            scholarship_data.append(
                {
                    "scholarship": scholarship,
                    "country_name": country.country_name,
                }
            )
        else:
            # Optional: handle scholarships with missing countries
            scholarship_data.append(
                {
                    "scholarship": scholarship,
                    "country_name": "Unknown Country (Deleted)",
                }
            )

    return render(
        request,
        "roottemplates/country_wise_scholarship_list.html",
        {"scholarship_data": scholarship_data},
    )


@login_required
@root_required
@permission_required(
    "visa.add_scholarships", "visa.change_scholarships", raise_exception=True
)
def edit_scholarship(request, scw_id):
    scholarship = get_object_or_404(CountryWises, pk=scw_id)
    countries = Countries.objects.all()

    if request.method == "POST":
        scw_text = request.POST.get("scw_text")
        scw_title = request.POST.get("scw_title")
        scw_whocanapply = request.POST.get("scw_whocanapply")
        scw_status = request.POST.get("scw_status")
        scw_country_id = request.POST.get("scw_country_id")

        if "scw_image" in request.FILES:
            scholarship.scw_image = request.FILES["scw_image"]

        scholarship.scw_text = scw_text
        scholarship.scw_title = scw_title
        scholarship.scw_whocanapply = scw_whocanapply
        scholarship.scw_status = scw_status
        scholarship.scw_country_id = scw_country_id
        scholarship.save()

        messages.success(request, "Consultant Wise Scholarship successfully updated.")

    scholarship_data = {
        "scw_text": scholarship.scw_text,
        "scw_whocanapply": scholarship.scw_whocanapply,
        "scw_status": scholarship.scw_status,
        "scw_country_id": scholarship.scw_country_id,
        "scw_image": scholarship.scw_image,
        "scw_title": scholarship.scw_title,  # Include the image in the data
    }

    return render(
        request,
        "roottemplates/edit_scholarship_form.html",
        {
            "scholarship_data": scholarship_data,
            "scw_id": scw_id,
            "countries": countries,
        },
    )


@login_required
@permission_required("visa.delete_scholarships", raise_exception=True)
@require_POST
def delete_scholarship(request, scw_id):
    scholarship = get_object_or_404(CountryWises, pk=scw_id)
    scholarship.delete()

    return JsonResponse(
        {
            "success": True,
            "message": "Scholarship deleted successfully",
            "scw_id": scw_id,
        }
    )


@login_required
@root_required
@permission_required("visa.add_scholarships", raise_exception=True)
def country_wise_scholarship(request):
    countries = Countries.objects.all()

    if request.method == "POST":
        scw_text = request.POST.get("scw_text")
        scw_whocanapply = request.POST.get("scw_whocanapply")
        scw_status = request.POST.get("scw_status")
        scw_country_id = request.POST.get("country_id")
        scw_image = request.FILES.get(
            "scw_image"
        )  # Assuming the file input name is 'scw_image'
        scw_title = request.POST.get("scw_title")

        try:
            scw_country_id = int(scw_country_id)
        except ValueError:
            messages.error(request, "Invalid country selected.")
            return render(
                request,
                "roottemplates/country_wise_scholarship.html",
                {"country": countries},
            )

        if scw_country_id:
            country_wise_check = CountryWises.objects.filter(
                scw_country_id=scw_country_id
            ).first()

            if country_wise_check is not None:
                print("error message printed")
                messages.error(
                    request,
                    f"The scholarship for this country already exists. Please go to edit to update the information",
                )
                return render(
                    request,
                    "roottemplates/country_wise_scholarship.html",
                    {"country": countries},
                )

            else:
                instance = CountryWises(
                    scw_text=scw_text,
                    scw_whocanapply=scw_whocanapply,
                    scw_status=scw_status,
                    scw_country_id=scw_country_id,
                    scw_image=scw_image,
                    created_at=timezone.now(),
                    updated_at=timezone.now(),
                )

                if scw_title:
                    instance.scw_title = scw_title

                if not scw_status:
                    instance.scw_status = 1

                operation_type = "created"
                instance.save()
                messages.success(
                    request, f"Country Wise Scholarship {operation_type} successfully."
                )

    instances = CountryWises.objects.all()

    return render(
        request,
        "roottemplates/country_wise_scholarship.html",
        {"instances": instances, "country": countries},
    )


@login_required
@root_required
@permission_required(
    "visa.add_scholarships", "visa.change_scholarships", raise_exception=True
)
def university_wise_scholarship(request):
    universities = UniversityWise.objects.all()

    if request.method == "POST":
        uw_text = request.POST.get("uw_text")
        uw_whocanapply = request.POST.get("uw_whocanapply")
        uw_status = request.POST.get("uw_status")
        uw_university_name = request.POST.get("uw_university_name")

        instance = UniversityWise(
            uw_text=uw_text,
            uw_whocanapply=uw_whocanapply,
            uw_status=uw_status,
            uw_university_name=uw_university_name,
            created_at=timezone.now(),
            updated_at=timezone.now(),
        )

        if not uw_status:
            instance.uw_status = 1

        operation_type = "created"
        instance.save()

        messages.success(
            request, f"University Wise Scholarship {operation_type} successfully."
        )

    instances = UniversityWise.objects.all()

    return render(
        request,
        "roottemplates/university_wise_scholarship.html",
        {"instances": instances, "universities": universities},
    )


@login_required
@root_required
def root_users_list(request):

    root_users = Users.objects.filter(user_role__in=[2, 3, 4])

    # Define the permission groups and their associated names
    permission_groups = {
        "log_entry_permissions": "Log Entry",
        "permission_permissions": "Permissions",
        # 'content_type_permissions': 'Content Type Permissions',
        # 'session_permissions': 'Session Permissions',
        # 'address_permissions': 'Address Permissions',
        "balance_permissions": "Accounts",
        # 'client_permissions': 'Client Permissions',
        # 'color_permissions': 'Color Permissions',
        # 'consultant_permissions': 'Consultant',
        # 'customize_permissions': 'Customize Permissions',
        "user_permissions": "Consultant",
        # 'district_permissions': 'District Permissions',
        # 'gallery_permissions': 'Gallery Permissions',
        # 'home_feedback_permissions': 'Home Feedback Permissions',
        # 'level_permissions': 'Level Permissions',
        # 'map_permissions': 'Map Permissions',
        "message_permissions": "Message",
        # 'migration_permissions': 'Migration Permissions',
        # 'notification_permissions': 'Notification Permissions',
        "offer_letter_permissions": "Apply Process",
        # 'permission_category_permissions': 'Permission Category Permissions',
        "rate_permissions": "Rate",
        # 'result_permissions': 'Result Permissions',
        # 'review_permissions': 'Review Permissions',
        "scholarship_permissions": "Scholarship",
        "student_permissions": "Students",
    }

    permission_group_mapping = {
        "auth.change_logentry": "log_entry_permissions",
        "auth.delete_logentry": "log_entry_permissions",
        "auth.add_logentry": "log_entry_permissions",
        "auth.view_logentry": "log_entry_permissions",
        "auth.add_group": "group_permissions",
        "auth.change_group": "group_permissions",
        "auth.delete_group": "group_permissions",
        "auth.view_group": "group_permissions",
        "auth.add_permission": "permission_permissions",
        "auth.change_permission": "permission_permissions",
        "auth.delete_permission": "permission_permissions",
        "auth.view_permission": "permission_permissions",
        "contenttypes.add_contenttype": "content_type_permissions",
        "contenttypes.change_contenttype": "content_type_permissions",
        "contenttypes.delete_contenttype": "content_type_permissions",
        "contenttypes.view_contenttype": "content_type_permissions",
        "sessions.add_session": "session_permissions",
        "sessions.change_session": "session_permissions",
        "sessions.delete_session": "session_permissions",
        "sessions.view_session": "session_permissions",
        "visa.add_address": "address_permissions",
        "visa.change_address": "address_permissions",
        "visa.delete_address": "address_permissions",
        "visa.view_address": "address_permissions",
        "visa.add_balance": "balance_permissions",
        "visa.change_balance": "balance_permissions",
        "visa.delete_balance": "balance_permissions",
        "visa.view_balance": "balance_permissions",
        "visa.add_client": "client_permissions",
        "visa.change_client": "client_permissions",
        "visa.delete_client": "client_permissions",
        "visa.view_client": "client_permissions",
        "visa.add_color": "color_permissions",
        "visa.change_color": "color_permissions",
        "visa.delete_color": "color_permissions",
        "visa.view_color": "color_permissions",
        "visa.add_consultantdetails": "consultant_permissions",
        "visa.change_consultantdetails": "consultant_permissions",
        "visa.delete_consultantdetails": "consultant_permissions",
        "visa.view_consultantdetails": "consultant_permissions",
        "visa.add_consultantimages": "consultant_permissions",
        "visa.change_consultantimages": "consultant_permissions",
        "visa.delete_consultantimages": "consultant_permissions",
        "visa.view_consultantimages": "consultant_permissions",
        "visa.add_consultantstatus": "consultant_permissions",
        "visa.change_consultantstatus": "consultant_permissions",
        "visa.delete_consultantstatus": "consultant_permissions",
        "visa.view_consultantstatus": "consultant_permissions",
        "visa.add_consultantwises": "consultant_permissions",
        "visa.change_consultantwises": "consultant_permissions",
        "visa.delete_consultantwises": "consultant_permissions",
        "visa.view_consultantwises": "consultant_permissions",
        "visa.add_country": "country_permissions",
        "visa.change_country": "country_permissions",
        "visa.delete_country": "country_permissions",
        "visa.view_country": "country_permissions",
        "visa.add_countryadds": "country_permissions",
        "visa.change_countryadds": "country_permissions",
        "visa.delete_countryadds": "country_permissions",
        "visa.view_countryadds": "country_permissions",
        "visa.add_countrywises": "country_permissions",
        "visa.change_countrywises": "country_permissions",
        "visa.delete_countrywises": "country_permissions",
        "visa.view_countrywises": "country_permissions",
        "visa.add_customizes": "customize_permissions",
        "visa.change_customizes": "customize_permissions",
        "visa.delete_customizes": "customize_permissions",
        "visa.view_customizes": "customize_permissions",
        "visa.add_custompermission": "custom_permission_permissions",
        "visa.change_custompermission": "custom_permission_permissions",
        "visa.delete_custompermission": "custom_permission_permissions",
        "visa.view_custompermission": "custom_permission_permissions",
        "visa.add_user": "user_permissions",
        "visa.change_user": "user_permissions",
        "visa.delete_user": "user_permissions",
        "visa.view_user": "user_permissions",
        "visa.add_district": "district_permissions",
        "visa.change_district": "district_permissions",
        "visa.delete_district": "district_permissions",
        "visa.view_district": "district_permissions",
        "visa.add_districts": "district_permissions",
        "visa.change_districts": "district_permissions",
        "visa.delete_districts": "district_permissions",
        "visa.view_districts": "district_permissions",
        "visa.add_explanation": "explanation_permissions",
        "visa.change_explanation": "explanation_permissions",
        "visa.delete_explanation": "explanation_permissions",
        "visa.view_explanation": "explanation_permissions",
        "visa.add_failedjobs": "failed_jobs_permissions",
        "visa.change_failedjobs": "failed_jobs_permissions",
        "visa.delete_failedjobs": "failed_jobs_permissions",
        "visa.view_failedjobs": "failed_jobs_permissions",
        "visa.add_galleries": "gallery_permissions",
        "visa.change_galleries": "gallery_permissions",
        "visa.delete_galleries": "gallery_permissions",
        "visa.view_galleries": "gallery_permissions",
        "visa.add_homefeedback": "home_feedback_permissions",
        "visa.change_homefeedback": "home_feedback_permissions",
        "visa.delete_homefeedback": "home_feedback_permissions",
        "visa.view_homefeedback": "home_feedback_permissions",
        "visa.add_levels": "level_permissions",
        "visa.change_levels": "level_permissions",
        "visa.delete_levels": "level_permissions",
        "visa.view_levels": "level_permissions",
        "visa.add_maps": "map_permissions",
        "visa.change_maps": "map_permissions",
        "visa.delete_maps": "map_permissions",
        "visa.view_maps": "map_permissions",
        "visa.add_message": "message_permissions",
        "visa.change_message": "message_permissions",
        "visa.delete_message": "message_permissions",
        "visa.view_message": "message_permissions",
        "visa.add_migrations": "migration_permissions",
        "visa.change_migrations": "migration_permissions",
        "visa.delete_migrations": "migration_permissions",
        "visa.view_migrations": "migration_permissions",
        "visa.add_notification": "notification_permissions",
        "visa.change_notification": "notification_permissions",
        "visa.delete_notification": "notification_permissions",
        "visa.view_notification": "notification_permissions",
        "visa.add_offerletters": "offer_letter_permissions",
        "visa.change_offerletters": "offer_letter_permissions",
        "visa.delete_offerletters": "offer_letter_permissions",
        "visa.view_offerletters": "offer_letter_permissions",
        "visa.add_passwordresets": "password_reset_permissions",
        "visa.change_passwordresets": "password_reset_permissions",
        "visa.delete_passwordresets": "password_reset_permissions",
        "visa.view_passwordresets": "password_reset_permissions",
        "visa.add_permissioncategories": "permission_category_permissions",
        "visa.change_permissioncategories": "permission_category_permissions",
        "visa.delete_permissioncategories": "permission_category_permissions",
        "visa.view_permissioncategories": "permission_category_permissions",
        "visa.add_rates": "rate_permissions",
        "visa.change_rates": "rate_permissions",
        "visa.delete_rates": "rate_permissions",
        "visa.view_rates": "rate_permissions",
        "visa.add_reply": "message_permissions",
        "visa.change_reply": "message_permissions",
        "visa.delete_reply": "message_permissions",
        "visa.view_reply": "message_permissions",
        "visa.add_results": "result_permissions",
        "visa.change_results": "result_permissions",
        "visa.delete_results": "result_permissions",
        "visa.view_results": "result_permissions",
        "visa.add_review": "review_permissions",
        "visa.change_review": "review_permissions",
        "visa.delete_review": "review_permissions",
        "visa.view_review": "review_permissions",
        "visa.add_scholarships": "scholarship_permissions",
        "visa.change_scholarships": "scholarship_permissions",
        "visa.delete_scholarships": "scholarship_permissions",
        "visa.view_scholarships": "scholarship_permissions",
        "visa.add_studentdetails": "student_details_permissions",
        "visa.change_studentdetails": "student_details_permissions",
        "visa.delete_studentdetails": "student_details_permissions",
        "visa.view_studentdetails": "student_details_permissions",
        "visa.add_students": "student_permissions",
        "visa.change_students": "student_permissions",
        "visa.delete_students": "student_permissions",
        "visa.view_students": "student_permissions",
        "visa.add_studentviewlog": "student_view_log_permissions",
        "visa.change_studentviewlog": "student_view_log_permissions",
        "visa.delete_studentviewlog": "student_view_log_permissions",
        "visa.view_studentviewlog": "student_view_log_permissions",
        "visa.add_thana": "thana_permissions",
        "visa.change_thana": "thana_permissions",
        "visa.delete_thana": "thana_permissions",
        "visa.view_thana": "thana_permissions",
        "visa.add_university": "university_permissions",
        "visa.change_university": "university_permissions",
        "visa.delete_university": "university_permissions",
        "visa.view_university": "university_permissions",
        "visa.add_universitywise": "university_wise_permissions",
        "visa.change_universitywise": "university_wise_permissions",
        "visa.delete_universitywise": "university_wise_permissions",
        "visa.view_universitywise": "university_wise_permissions",
        "visa.add_upazilas": "upazilas_permissions",
        "visa.change_upazilas": "upazilas_permissions",
        "visa.delete_upazilas": "upazilas_permissions",
        "visa.view_upazilas": "upazilas_permissions",
        "visa.add_users": "users_permissions",
        "visa.change_users": "users_permissions",
        "visa.delete_users": "users_permissions",
        "visa.view_users": "users_permissions",
        "visa.add_usersession": "user_session_permissions",
        "visa.change_usersession": "user_session_permissions",
        "visa.delete_usersession": "user_session_permissions",
        "visa.view_usersession": "user_session_permissions",
    }

    grouped_permissions = {}

    for codename, group_name in permission_groups.items():
        if group_name not in grouped_permissions:
            grouped_permissions[group_name] = []

        try:
            permission = Permission.objects.get(codename=codename)
            grouped_permissions[group_name].append((permission.id, permission.name))
        except Permission.DoesNotExist:
            pass

    context = {
        "root_users": root_users,
        "grouped_permissions": grouped_permissions,
        "permission_groups": permission_groups,
        "group_names": permission_groups.values(),
    }

    return render(request, "roottemplates/rootuser_list.html", context)


@permission_required("visa.add_users", raise_exception=True)
@login_required
@root_required
def create_root(request):
    if request.method == "POST":
        full_name = request.POST.get("full_name")
        email = request.POST.get("email")
        phone = request.POST.get("phone")
        raw_password = request.POST.get("password")

        try:
            # Check if email or phone already exist in either Users or CustomUser model
            if (
                Users.objects.filter(email=email).exists()
                or CustomUser.objects.filter(email=email).exists()
            ):
                messages.error(request, "Email already exists")
            elif (
                Users.objects.filter(phone=phone).exists()
                or CustomUser.objects.filter(phone=phone).exists()
            ):
                messages.error(request, "Phone number already exists")
            else:
                # Create a new Users instance
                new_users_instance = Users.objects.create(
                    full_name=full_name,
                    email=email,
                    phone=phone,
                    password=make_password(raw_password),
                    user_role=2,
                    created_at=timezone.now(),
                    updated_at=timezone.now(),
                )

                # Create a new CustomUser instance with the same ID as Users instance
                user = CustomUser.objects.create(
                    id=new_users_instance.id,
                    email=email,
                    username=full_name,
                    user_type=0,
                    phone=phone,
                )
                user.set_password(raw_password)  # Set password
                user.save()

                messages.success(request, "Root user created successfully.")
                return redirect("root_users_list")

        except Exception as e:
            messages.error(request, f"An error occurred: {e}")

    return render(request, "roottemplates/create_root.html")


def some_condition_is_met():

    return True


def grant_permission(request, user_id):
    if request.method == "POST":
        try:
            # Retrieve the CustomUser instance
            user_instance = CustomUser.objects.get(id=user_id)

            # Get the selected permission groups from the request
            selected_groups = request.POST.getlist("groups")

            # Map group names to their corresponding permission IDs
            group_permissions = {
                "Log Entry": [
                    "auth.add_logentry",
                    "auth.change_logentry",
                    "auth.delete_logentry",
                    "auth.view_logentry",
                ],
                "Permissions": [
                    "auth.add_permission",
                    "auth.change_permission",
                    "auth.delete_permission",
                    "auth.view_permission",
                ],
                "Accounts": [
                    "visa.add_balances",
                    "visa.change_balances",
                    "visa.delete_balances",
                    "visa.view_balances",
                    "visa.add_rates",
                    "visa.change_rates",
                    "visa.delete_rates",
                    "visa.view_rates",
                ],
                "Consultant": [
                    "visa.add_users",
                    "visa.change_users",
                    "visa.delete_users",
                    "visa.view_users",
                ],
                "Message": [
                    "visa.add_message",
                    "visa.change_message",
                    "visa.delete_message",
                    "visa.view_message",
                ],
                "Apply Process": [
                    "visa.add_offerletters",
                    "visa.change_offerletters",
                    "visa.delete_offerletters",
                    "visa.view_offerletters",
                ],
                "Rate": [
                    "visa.add_rates",
                    "visa.change_rates",
                    "visa.delete_rates",
                    "visa.view_rates",
                ],
                "Scholarship": [
                    "visa.add_scholarships",
                    "visa.change_scholarships",
                    "visa.delete_scholarships",
                    "visa.view_scholarships",
                ],
                "Students": [
                    "visa.add_students",
                    "visa.change_students",
                    "visa.delete_students",
                    "visa.view_students",
                ],
            }

            # Get the current permissions of the user
            current_permissions = user_instance.user_permissions.values_list(
                "codename", flat=True
            )

            # Determine permissions to be added and removed
            permissions_to_add = []
            permissions_to_remove = []
            for group_name, permissions in group_permissions.items():
                if group_name in selected_groups:
                    permissions_to_add.extend(permissions)
                else:
                    permissions_to_remove.extend(permissions)

            # Remove permissions not included in selected groups
            for permission_codename in permissions_to_remove:
                try:
                    codename_without_prefix = permission_codename.split(".")[-1]
                    if codename_without_prefix in current_permissions:
                        permission = Permission.objects.get(
                            codename=codename_without_prefix
                        )
                        user_instance.user_permissions.remove(permission)
                except Permission.DoesNotExist:
                    pass  # Handle the case where permission does not exist

            # Add permissions from selected groups
            for permission_codename in permissions_to_add:
                try:
                    codename_without_prefix = permission_codename.split(".")[-1]
                    if codename_without_prefix not in current_permissions:
                        permission = Permission.objects.get(
                            codename=codename_without_prefix
                        )
                        user_instance.user_permissions.add(permission)
                except Permission.DoesNotExist:
                    pass  # Handle the case where permission does not exist

            # Retrieve existing permissions of the user
            existing_permissions = user_instance.user_permissions.values_list(
                "codename", flat=True
            )

            # Match group names with existing permissions and toggle checked status
            matched_group_names = []
            for group_name, permissions in group_permissions.items():
                if any(
                    permission.split(".")[-1] in existing_permissions
                    for permission in permissions
                ):
                    matched_group_names.append(group_name)

            # Check if any permissions were granted
            if permissions_to_add:
                return JsonResponse(
                    {
                        "message": "Permissions updated successfully.",
                        "matched_group_names": matched_group_names,
                    }
                )
            else:
                return JsonResponse({"error": "No permissions selected."}, status=400)
        except CustomUser.DoesNotExist:
            return JsonResponse({"error": "User does not exist"}, status=404)
    else:
        return JsonResponse({"error": "Invalid request method."}, status=400)


@login_required
def get_existing_permissions(request, user_id):
    try:
        user_instance = get_object_or_404(CustomUser, id=user_id)
        existing_permissions = user_instance.user_permissions.values_list(
            "codename", flat=True
        )
        group_permissions = {
            "add_logentry": "Log Entry",
            "change_logentry": "Log Entry",
            "delete_logentry": "Log Entry",
            "view_logentry": "Log Entry",
            "add_balances": "Accounts",
            "change_balances": "Accounts",
            "delete_balances": "Accounts",
            "view_balances": "Accounts",
            "add_users": "Consultant",
            "change_users": "Consultant",
            "delete_users": "Consultant",
            "view_users": "Consultant",
            "add_message": "Message",
            "change_message": "Message",
            "delete_message": "Message",
            "view_message": "Message",
            "add_offerletters": "Apply Process",
            "change_offerletters": "Apply Process",
            "delete_offerletters": "Apply Process",
            "view_offerletters": "Apply Process",
            "add_rates": "Rate",
            "change_rates": "Rate",
            "delete_rates": "Rate",
            "view_rates": "Rate",
            "add_reply": "Reply",
            "change_reply": "Reply",
            "delete_reply": "Reply",
            "view_reply": "Reply",
            "add_scholarships": "Scholarship",
            "change_scholarships": "Scholarship",
            "delete_scholarships": "Scholarship",
            "view_scholarships": "Scholarship",
            "add_students": "Students",
            "change_students": "Students",
            "delete_students": "Students",
            "view_students": "Students",
            "add_permission": "Permissions",
            "change_permission": "Permissions",
            "delete_permission": "Permissions",
            "view_permission": "Permissions",
        }

        matched_group_names = set()
        for codename in existing_permissions:
            if codename in group_permissions:
                matched_group_names.add(group_permissions[codename])

        return JsonResponse({"existing_permissions": list(matched_group_names)})
    except CustomUser.DoesNotExist:
        return JsonResponse({"error": "User does not exist"}, status=404)


@login_required
@root_required
@permission_required("visa.add_users", "visa.change_users", raise_exception=True)
def root_consultant_list(request):
    # Filter users based on those who are consultants (role 5) 
    # and have a status indicating they are pending (null or 0).
    # We exclude approved consultant accounts by their actual consultant identity
    # fields, not by raw cross-table ids.
    approved_consultant_accounts = CustomUser.objects.filter(user_type=1)
    rootconsultant = (
        Users.objects.filter(user_role=5)
        .filter(Q(active_status__isnull=True) | Q(active_status=0))
        .exclude(
            email__in=approved_consultant_accounts.exclude(email__isnull=True).values(
                "email"
            )
        )
        .exclude(
            phone__in=approved_consultant_accounts.exclude(phone__isnull=True).values(
                "phone"
            )
        )
        .order_by("company_name")
    )

    context = {
        "rootconsultant": rootconsultant,
        "pending_count": rootconsultant.count(),
    }
    return render(request, "roottemplates/rootconsultant_list.html", context)


@permission_required("visa.add_users", "visa.change_users", raise_exception=True)
@login_required
def grant_permission_consultant(request, user_id):
    try:
        # Get the Users instance using user_id
        user_instance = Users.objects.get(pk=user_id)
        # Check if permission is granted
        if some_condition_is_met():
            with transaction.atomic():
                new_custom_user = CustomUser.objects.create(
                    email=user_instance.email,
                    password=user_instance.password,
                    user_type=1,
                    phone=user_instance.phone,
                    last_active=timezone.now(),
                )
                user_instance.consultant_user = new_custom_user
                user_instance.save()
                ConsultantDetails.objects.create(
                    consultant_id=user_instance.id,
                    # Add other fields as needed
                )
            # Set the active_status to 1 when permission is granted
            user_instance.active_status = 1
            user_instance.save()
            messages.success(request, "Consultant created successfully.")
        else:
            # Set the active_status to 0 when rejecting the consultant
            user_instance.active_status = 0
            user_instance.save()
            messages.success(
                request, "Permission not granted for Consultant. Consultant rejected."
            )
    except Users.DoesNotExist:
        messages.error(request, "Consultant not found.")
    return redirect("root_consultant_list")


@login_required
@permission_required("visa.add_users", "visa.delete_users", raise_exception=True)
@require_POST
def reject_consultant(request, user_id):
    try:
        user_instance = Users.objects.get(pk=user_id)
        consultant_details_ids = {user_instance.id}
        linked_custom_users = []

        if user_instance.consultant_user_id:
            linked_custom_users.append(user_instance.consultant_user)
            consultant_details_ids.add(user_instance.consultant_user_id)

        additional_custom_users = CustomUser.objects.filter(
            user_type=1
        ).filter(
            Q(email=user_instance.email) | Q(phone=user_instance.phone)
        )

        for custom_user in additional_custom_users:
            consultant_details_ids.add(custom_user.id)
            if all(existing.id != custom_user.id for existing in linked_custom_users):
                linked_custom_users.append(custom_user)

        with transaction.atomic():
            ConsultantDetails.objects.filter(
                consultant_id__in=list(consultant_details_ids)
            ).delete()

            user_instance.delete()

            for custom_user in linked_custom_users:
                custom_user.delete()

        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse(
                {
                    "success": True,
                    "message": "Consultant rejected and removed successfully.",
                }
            )
        messages.success(request, "Consultant rejected and removed successfully.")
    except Users.DoesNotExist:
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({"success": False, "message": "Consultant not found."}, status=404)
        messages.error(request, "Consultant not found.")
    except Exception as exc:
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse(
                {"success": False, "message": str(exc)},
                status=500,
            )
        messages.error(request, "An error occurred while rejecting the consultant.")

    return redirect("root_consultant_list")


@login_required
@permission_required("visa.add_users", "visa.delete_users", raise_exception=True)
def activeconsultant(request):
    active_consultants = Users.objects.filter(
        user_role=5, active_status__in=[1, 3, 4, 5]
    ).select_related("consultant_user")

    consultant_data = [
        {
            "id": user.id,
            "company_name": user.company_name,
            "full_name": user.full_name,
            "email": user.email,
            "phone": user.phone,
            "registration": user.created_at.strftime("%Y-%m-%d %H:%M:%S")
            if user.created_at
            else None,
            "last_active": user.consultant_user.last_active
            if user.consultant_user
            else None,
        }
        for user in active_consultants
    ]

    # Sort consultant_data by full_name in ascending order
    consultant_data_sorted = sorted(
        consultant_data, key=lambda x: (x["full_name"], x["company_name"])
    )

    return JsonResponse({"consultants": consultant_data_sorted}, safe=False)


@login_required
@permission_required("visa.add_users", "visa.delete_users", raise_exception=True)
def active_consultant_details(request, user_id):
    consultant = get_object_or_404(Users, id=user_id, active_status__in=[1, 3, 4, 5])

    consultant_data = {
        "id": consultant.id,
        "full_name": consultant.full_name,
        "email": consultant.email,
        "phone": consultant.phone,
        "company_name": consultant.company_name,
        "website": consultant.website,
        "address": consultant.address,
    }

    return JsonResponse({"consultant": consultant_data})


@login_required
@permission_required("visa.add_users", "visa.delete_users", raise_exception=True)
def suspend_account(request, user_id):
    # Get the user to be suspendedd
    user = get_object_or_404(Users, id=user_id)

    # Suspend the account (update the active_status or any other relevant field)
    user.active_status = 2
    user.suspension_time = (
        timezone.now()
    )  # Assuming 2 represents suspended status, adjust as needed
    user.save()

    return JsonResponse({"message": "Account suspended successfully"})


@login_required
@permission_required("visa.add_users", "visa.delete_users", raise_exception=True)
def suspend_list(request):
    # Retrieve a list of suspended users
    suspended_users = Users.objects.filter(active_status=2).order_by(
        "company_name"
    )  # Assuming 2 represents suspended status, adjust as needed

    # Create a list of dictionaries containing user information
    user_list = [
        {
            "id": user.id,
            "company_name": user.company_name,
            "full_name": user.full_name,
            "email": user.email,
            "phone": user.phone,
            "suspension_time": user.suspension_time.strftime("%Y-%m-%d %H:%M:%S")
            if user.suspension_time
            else None,
        }
        for user in suspended_users
    ]

    # Return a JSON response with the user list
    return JsonResponse({"suspended_users": user_list})


@login_required
@permission_required("visa.add_users", "visa.delete_users", raise_exception=True)
def suspended_consultant_details(request, user_id):
    consultant = get_object_or_404(Users, id=user_id, active_status=2)

    consultant_data = {
        "full_name": consultant.full_name,
        "email": consultant.email,
        "phone": consultant.phone,
        "company_name": consultant.company_name,
        "website": consultant.website,
        "address": consultant.address,
    }

    return JsonResponse({"consultant": consultant_data})


@login_required
@permission_required("visa.add_users", "visa.delete_users", raise_exception=True)
def free_account(request, user_id):

    user = get_object_or_404(Users, id=user_id, user_role=5)
    user.active_status = 3
    user.save()
    return JsonResponse({"message": "Free account processed successfully"})


@login_required
@permission_required("visa.add_users", "visa.delete_users", raise_exception=True)
def free_list(request):

    free_users = Users.objects.filter(active_status=3).order_by("company_name")

    user_list = [
        {
            "id": user.id,
            "company_name": user.company_name,
            "full_name": user.full_name,
            "email": user.email,
            "phone": user.phone,
        }
        for user in free_users
    ]

    return JsonResponse({"free_users": user_list})


@login_required
@permission_required("visa.add_users", "visa.delete_users", raise_exception=True)
def free_consultant_details(request, user_id):
    consultant = get_object_or_404(Users, id=user_id, active_status=3)

    consultant_data = {
        "full_name": consultant.full_name,
        "email": consultant.email,
        "phone": consultant.phone,
        "company_name": consultant.company_name,
        "website": consultant.website,
        "address": consultant.address,
    }

    return JsonResponse({"consultant": consultant_data})


@login_required
@permission_required("visa.add_users", "visa.delete_users", raise_exception=True)
def activate_basic_account(request, user_id):
    # Get the user with status 2 and user role 4 (adjust as needed)
    user = get_object_or_404(Users, id=user_id, user_role=5)
    user.active_status = (
        4  # Assuming 4 represents an active status for basic users, adjust as needed
    )
    user.save()
    return JsonResponse({"message": "Basic account activated successfully"})


@login_required
@permission_required("visa.add_users", "visa.delete_users", raise_exception=True)
def basic_list(request):
    # Retrieve a list of users with status 2 and user role 4 (adjust as needed)
    basic_users = Users.objects.filter(active_status=4).order_by("company_name")

    # Create a list of dictionaries containing user information
    user_list = [
        {
            "id": user.id,
            "company_name": user.company_name,
            "full_name": user.full_name,
            "email": user.email,
            "phone": user.phone,
            # Include any additional fields as needed
        }
        for user in basic_users
    ]

    # Return a JSON response with the user list
    return JsonResponse({"basic_users": user_list})


@login_required
@permission_required("visa.add_users", "visa.delete_users", raise_exception=True)
def basic_user_details(request, user_id):
    consultant = get_object_or_404(Users, id=user_id, active_status=4)

    # Create a dictionary containing user details
    consultant_data = {
        "full_name": consultant.full_name,
        "email": consultant.email,
        "phone": consultant.phone,
        "company_name": consultant.company_name,
        # Include any additional fields as needed
    }

    # Return a JSON response with the user details
    return JsonResponse({"consultant": consultant_data})


@login_required
@permission_required("visa.add_users", "visa.delete_users", raise_exception=True)
def activate_premium_account(request, user_id):
    # Get the user with status 2 and user role 4 (adjust as needed)
    user = get_object_or_404(Users, id=user_id, user_role=5)
    user.active_status = (
        5  # Assuming 4 represents an active status for basic users, adjust as needed
    )
    user.save()
    return JsonResponse({"message": "Preminum account activated successfully"})


@login_required
@permission_required("visa.add_users", "visa.delete_users", raise_exception=True)
def premium_list(request):
    # Retrieve a list of users with status 2 and user role 4 (adjust as needed)
    premium_users = Users.objects.filter(active_status=5).order_by("company_name")

    # Create a list of dictionaries containing user information
    user_list = [
        {
            "id": user.id,
            "company_name": user.company_name,
            "full_name": user.full_name,
            "email": user.email,
            "phone": user.phone,
            # Include any additional fields as needed
        }
        for user in premium_users
    ]

    # Return a JSON response with the user list
    return JsonResponse({"premium_users": user_list})


@login_required
@permission_required("visa.add_users", "visa.delete_users", raise_exception=True)
def preimum_user_details(request, user_id):
    consultant = get_object_or_404(Users, id=user_id, active_status=5)

    # Create a dictionary containing user details
    consultant_data = {
        "full_name": consultant.full_name,
        "email": consultant.email,
        "phone": consultant.phone,
        "company_name": consultant.company_name,
        # Include any additional fields as needed
    }

    # Return a JSON response with the user details
    return JsonResponse({"consultant": consultant_data})


@login_required
@permission_required("visa.add_users", "visa.delete_users", raise_exception=True)
def activate_account(request, user_id):
    user = get_object_or_404(Users, id=user_id)

    user.active_status = 1
    user.save()

    return JsonResponse({"message": "Account activated successfully"})


# @login_required
# @permission_required('visa.add_students', 'visa.change_students', raise_exception=True)
# def inactive_students_list(request):

#     inactive_students = Students.objects.filter(status=0).order_by('full_name')


#     student_list = [{
#         'id': student.id,
#         'full_name': student.full_name,
#         'email': student.email,
#         'phone': student.phone,
#         'registration': student.created_at.strftime('%Y-%m-%d %H:%M:%S') if student.created_at else None,

#         'status': student.status
#     } for student in inactive_students]


#     context = {'inactive_students': student_list}


#     return render(request, 'roottemplates/student_list.html', context)


@login_required
@permission_required("visa.add_students", "visa.change_students", raise_exception=True)
def suspended_students_list(request):

    suspend_students = Students.objects.filter(status=3).order_by("full_name")

    student_list = [
        {
            "id": student.id,
            "full_name": student.full_name,
            "email": student.email,
            "phone": student.phone,
            "registration": student.created_at.strftime("%Y-%m-%d %H:%M:%S")
            if student.created_at
            else None,
            "status": student.status,
        }
        for student in suspend_students
    ]

    context = {"suspend_students": student_list}

    return render(request, "roottemplates/student_list.html", context)


@login_required
@permission_required("visa.change_students", raise_exception=True)
def make_suspend(request, student_id):
    try:
        student = Students.objects.get(pk=student_id)
        student.status = (
            3  # Update status to suspended (assuming 3 represents suspended status)
        )
        student.save()
        return JsonResponse(
            {
                "success": True,
                "message": f"Student {student.full_name}'s account has been suspended.",
            }
        )
    except Students.DoesNotExist:
        return JsonResponse({"success": False, "message": "Student not found."})
    except Exception as e:
        return JsonResponse({"success": False, "message": str(e)})


@login_required
@permission_required("visa.add_students", "visa.change_students", raise_exception=True)
def students_details(request, student_id):

    student = get_object_or_404(Students, id=student_id)
    print(f"Type of 'status': {type(student.status)}")

    student_details = {
        "id": student.id,
        "full_name": student.full_name,
        "email": student.email,
        "phone": student.phone,
        "user_type": student.user_type,
        "gender": student.gender,
        "status": student.status,
        "created_at": student.created_at.strftime("%Y-%m-%d %H:%M:%S")
        if student.created_at
        else None,
    }
    print("student_details:", student_details)

    return JsonResponse({"student_details": student_details})


@login_required
@permission_required("visa.add_students", "visa.change_students", raise_exception=True)
def activate_student_account(request, student_id):
    student = get_object_or_404(Students, id=student_id)

    student.status = 1
    student.save()

    return JsonResponse({"message": "Student account activated successfully"})


@permission_required("visa.add_students", "visa.change_students", raise_exception=True)
@login_required
def active_student_list(request):

    active_students = Students.objects.filter(status=1).order_by("full_name")
    active_students_details = []
    for student in active_students:
        student_details = {
            "id": student.id,
            "full_name": student.full_name,
            "email": student.email,
            "phone": student.phone,
            "gender": student.gender,
            "created_at": student.created_at.strftime("%Y-%m-%d %H:%M:%S")
            if student.created_at
            else None,
        }
        active_students_details.append(student_details)

    # Return a JSON response with the list of active student details
    return JsonResponse({"active_students_details": active_students_details})


@permission_required("visa.add_students", "visa.change_students", raise_exception=True)
@login_required
def active_student_details(request, student_id):
    try:
        student = Students.objects.get(id=student_id)

        # Fetch related Results
        result = Results.objects.filter(student_id=student_id).first()
        masters_degrees = MastersDegree.objects.filter(student_id=student_id).order_by(
            "-passing_year"
        )[:2]
        other_certifications = OtherCertification.objects.filter(
            student_id=student_id
        ).order_by("-passing_year")
        # results_data = serialize('json', result)

        exam_type = {}

        # Mapping for secondary
        secondary_map = {1: "SSC", 2: "O Level", 3: "Dhakhil"}

        # Mapping for higher
        higher_map = {1: "HSC", 2: "A Level", 3: "Vocational"}

        undergraduation_map = {1: "Undergraduation"}

        master_degrees_dict = {"masters": {}}
        no_of_masters_degrees = len(masters_degrees)

        for index, master_degree in enumerate(masters_degrees):
            master_str = f"master_degree_{index + 1};{master_degree.department}"
            master_degrees_dict["masters"][master_str] = master_degree.department

        print("master_degrees_dict: ", master_degrees_dict)

        secondary_value = secondary_map.get(result.secondary) if result else None
        higher_value = higher_map.get(result.higher) if result else None
        undergraduation_value = (
            undergraduation_map.get(result.undergraduation) if result else None
        )

        if result.secondary == 1:
            secondary_exam_type = "SSC"

        elif result.secondary == 2:
            secondary_exam_type = "O level"

        elif result.secondary == 3:
            secondary_exam_type = "Dhakhil"

        else:
            higher_exam_type = "N/A"

        if result.higher == 1:
            higher_exam_type = "HSC"

        elif result.higher == 2:
            higher_exam_type = "A level"

        elif result.higher == 3:
            higher_exam_type = "Vocational"

        elif result.higher == 4:
            higher_exam_type = "Diploma"

        else:
            higher_exam_type = "N/A"

        # student result starts
        # Secondary education data
        education_data = []

        secondary_data = {
            "level": secondary_exam_type,
            "institute_name": "N/A",
            "board": result.secondary_board,
            "result": result.secondary_result,
            "roll_no": result.secondary_roll_no if result.secondary_roll_no else "N/A",
            "reg_no": result.secondary_reg_no if result.secondary_reg_no else "N/A",
            "certificate_no": result.secondary_certificate_no
            if result.secondary_certificate_no
            else "N/A",
            "passing_year": result.secondary_passing_year
            if result.secondary_passing_year
            else "N/A",
            "certificate_copy": result.secondary_certificate_copy.url
            if result.secondary_certificate_copy
            else "N/A",
            "created_at": result.created_at if result.created_at else "N/A",
            "updated_at": result.updated_at if result.updated_at else "N/A",
            "verification_status": result.secondary_verification_status,
            "rejection_note": result.secondary_rejection_note,
            "result_id": result.id,
        }
        education_data.append(secondary_data)

        # Higher education data
        higher_data = {
            "level": higher_exam_type,
            "institute_name": "N/A",
            "board": result.higher_board,
            "result": result.higher_result,
            "roll_no": result.higher_roll_no if result.higher_roll_no else "N/A",
            "reg_no": result.higher_reg_no if result.higher_reg_no else "N/A",
            "certificate_no": result.higher_certificate_no
            if result.higher_certificate_no
            else "N/A",
            "passing_year": result.higher_passing_year
            if result.higher_passing_year
            else "N/A",
            "certificate_copy": result.higher_certificate_copy.url
            if result.higher_certificate_copy
            else "N/A",
            "created_at": result.created_at if result.created_at else "N/A",
            "updated_at": result.updated_at if result.updated_at else "N/A",
            "verification_status": result.higher_verification_status,
            "rejection_note": result.higher_rejection_note,
            "result_id": result.id,
        }
        education_data.append(higher_data)

        # Undergraduate education data
        print("undergraduation unversity name: ", result.university_name)
        if result.university_name:
            undergraduate_data = {
                "level": "Undergraduate",
                "institute_name": result.university_name
                if result.university_name
                else "N/A",
                "board": result.undergraduation_board,
                "result": result.undergraduation_result,
                "roll_no": "N/A",
                "reg_no": "N/A",
                "certificate_no": "N/A",
                "passing_year": result.undergraduation_passing_year
                if result.undergraduation_passing_year
                else "N/A",
                "certificate_copy": result.undergraduation_certificate_copy.url
                if result.undergraduation_certificate_copy
                else "N/A",
                "rejection_note": result.undergraduation_rejection_note,
                "verification_status": result.undergraduation_verification_status,
                "created_at": result.created_at if result.created_at else "N/A",
                "updated_at": result.updated_at if result.updated_at else "N/A",
                "result_id": result.id,
            }

            education_data.append(undergraduate_data)

        # Masters degree
        if masters_degrees.exists():
            for master in masters_degrees:
                masters_data = {
                    "level": f"Masters: {master.department}",
                    "institute_name": master.university if master.university else "N/A",
                    "board": "UGC",
                    "result": master.result if master.result else "N/A",
                    "roll_no": "N/A",
                    "reg_no": "N/A",
                    "certificate_no": "N/A",
                    "passing_year": master.passing_year
                    if master.passing_year
                    else "N/A",
                    "certificate_copy": master.certificate_copy.url
                    if master.certificate_copy
                    else "N/A",
                    "result_id": master.id,
                    "verification_status": master.verification_status,
                    "rejection_note": master.rejection_note,
                    "created_at": result.created_at if result.created_at else "N/A",
                    "updated_at": result.updated_at if result.updated_at else "N/A",
                }

                education_data.append(masters_data)

        # Other Certifications/Courses
        if other_certifications.exists():
            for course in other_certifications:
                course_data = {
                    "level": course.course_name.name,
                    "institute_name": course.institute if course.institute else "N/A",
                    "board": "UGC",
                    "result": course.result if course.result else "N/A",
                    "roll_no": "N/A",
                    "reg_no": "N/A",
                    "certificate_no": "N/A",
                    "passing_year": course.passing_year
                    if course.passing_year
                    else "N/A",
                    "certificate_copy": course.certificate_copy.url
                    if course.certificate_copy
                    else "N/A",
                    "result_id": course.id,
                    "verification_status": course.verification_status,
                    "rejection_note": course.rejection_note,
                    "created_at": course.created_at if course.created_at else "N/A",
                    "updated_at": course.updated_at if course.updated_at else "N/A",
                }

                education_data.append(course_data)

        # student result ends

        student_details = {
            "id": student.id,
            "full_name": student.full_name,
            "email": student.email,
            "phone": student.phone,
            "address": student.address,
            "status": student.status,
            "created_at": student.created_at.strftime("%Y-%m-%d %H:%M:%S"),
            # 'results': results_data,
        }

        print("education data: ", education_data)

        # for education_reuslt in education_data:
        all_verified = all(
            entry.get("verification_status") == "verified" for entry in education_data
        )

        if all_verified:
            all_result_verification = "verified"

        else:
            all_result_verification = "pending"

        print("all_result_verification: ", all_result_verification)

        return JsonResponse(
            {
                "student_details": student_details,
                # 'results_details': results_details,
                "secondary_value": secondary_value,
                "higher_value": higher_value,
                "undergraduation_value": undergraduation_value,
                "master_degrees_dict": master_degrees_dict,
                "education_data": education_data,
                "all_result_verification": all_result_verification,
            }
        )

    except Students.DoesNotExist:
        return JsonResponse({"error": "Student not found"}, status=404)


@login_required
def update_verification_status(request):
    if request.method == "GET":
        # Extract data from the request query parameters
        result_id = request.GET.get("result_id")
        verification_status = request.GET.get("action")
        verification_type = request.GET.get("verification_type")
        rejection_note = request.GET.get("rejection_note")

        print("--------------------------------------")
        print("result_id: ", result_id)
        print("verification_status: ", verification_status)
        print("verification_type: ", verification_type)
        print("rejection_note: ", rejection_note)
        print("--------------------------------------")

        course_names = OtherCertification.objects.all()
        course_names_list = [
            certification.course_name.name for certification in course_names
        ]
        print("course_names_list: ", course_names_list)

        if "Masters" in verification_type:
            result = get_object_or_404(MastersDegree, id=result_id)

        elif verification_type in course_names_list:
            print("verification_type in other course: ", verification_type)
            result = get_object_or_404(OtherCertification, id=result_id)

        # Get the corresponding result object
        else:
            result = get_object_or_404(Results, id=result_id)
            print("student is: ", result.student_id)

        # Ensure verification status is one of the valid choices
        valid_statuses = ["pending", "verified", "rejected"]

        if verification_status not in valid_statuses:
            return JsonResponse(
                {"error": "Invalid verification status provided."}, status=400
            )

        # Determine the verification status field based on the verification type
        if (
            verification_type == "SSC"
            or verification_type == "O level"
            or verification_type == "Dhakhil"
        ):
            result.secondary_verification_status = verification_status
            result.secondary_rejection_note = rejection_note
            result.save()

        elif (
            verification_type == "HSC"
            or verification_type == "A level"
            or verification_type == "Vocational"
            or verification_type == "Diploma"
        ):
            result.higher_verification_status = verification_status
            result.higher_rejection_note = rejection_note
            result.save()

        elif verification_type == "Undergraduate":
            result.undergraduation_verification_status = verification_status
            result.undergraduation_rejection_note = rejection_note
            result.save()

        elif "Masters" in verification_type:
            print("verification_type in masters: ", verification_type)
            masters_degree = get_object_or_404(MastersDegree, id=result_id)
            print("masters_degree: ", masters_degree.verification_status)
            print("verification_status in masters courses: ", verification_status)
            masters_degree.verification_status = verification_status
            masters_degree.rejection_note = rejection_note
            masters_degree.save()
            print(
                "verification_status in masters courses after saving: ",
                masters_degree.verification_status,
            )

        elif verification_type in course_names_list:
            other_certification = get_object_or_404(OtherCertification, id=result_id)
            print("verification_status in other courses: ", verification_status)
            other_certification.verification_status = verification_status
            other_certification.rejection_note = rejection_note
            other_certification.save()

        else:
            return JsonResponse(
                {"error": "Invalid verification type provided."}, status=400
            )

        return JsonResponse(
            {
                "success": True,
                "message": f"{verification_type.capitalize()} verification status updated to {verification_status}.",
            }
        )

    else:
        return JsonResponse({"error": "Invalid request method."}, status=405)


@permission_required("visa.add_students", "visa.change_students", raise_exception=True)
@login_required
def verify_student_account(request, student_id):
    student = get_object_or_404(Students, id=student_id)

    student.status = 2
    student.save()

    # Check if the student_id and consultant_id match in StudentDetails
    student_details = StudentDetails.objects.filter(dets_regs_id=student_id)
    if student_details.exists():
        student_details = student_details.first()
        consultant_id = (
            request.user.id
        )  # Assuming consultant_id comes from the request user
        consultant_status, created = ConsultantStatus.objects.get_or_create(
            student=student_details, consultant_id=consultant_id
        )
        consultant_status.status = StudentDetails.VIEWED  # Set status to VIEWED (1)
        consultant_status.save()

        # Save the student in level 1
        # level, created = Levels.objects.get_or_create(student_id=student_id)
        # level.level_1 = student_id
        # level.status = 1
        # level.save()

    return JsonResponse({"message": "Student account activated successfully"})


@login_required
@permission_required("visa.add_students", "visa.change_students", raise_exception=True)
def verify_student_list(request):
    # Filter students with status code 1 (Active)
    verify_students = Students.objects.filter(status=2).order_by("full_name")

    # Prepare a list of active student details
    verify_students_details = []
    for student in verify_students:
        student_details = {
            "id": student.id,
            "full_name": student.full_name,
            "email": student.email,
            "phone": student.phone,
            "gender": student.gender,
            "created_at": student.created_at.strftime("%Y-%m-%d %H:%M:%S")
            if student.created_at
            else None,
        }
        verify_students_details.append(student_details)

    # Return a JSON response with the list of active student details
    return JsonResponse({"verify_students_details": verify_students_details})


@login_required
@permission_required("visa.add_students", "visa.change_students", raise_exception=True)
@login_required
@permission_required("visa.add_students", "visa.change_students", raise_exception=True)
def verify_student_details(request, student_id):
    try:
        student = Students.objects.get(id=student_id)

        # Fetch related Results
        result = Results.objects.filter(student_id=student_id).first()
        masters_degrees = MastersDegree.objects.filter(student_id=student_id).order_by(
            "-passing_year"
        )[:2]
        other_certifications = OtherCertification.objects.filter(
            student_id=student_id
        ).order_by("-passing_year")
        # results_data = serialize('json', result)

        exam_type = {}

        # Mapping for secondary
        secondary_map = {1: "SSC", 2: "O Level", 3: "Dhakhil"}

        # Mapping for higher
        higher_map = {1: "HSC", 2: "A Level", 3: "Vocational"}

        undergraduation_map = {1: "Undergraduation"}

        master_degrees_dict = {"masters": {}}
        no_of_masters_degrees = len(masters_degrees)

        for index, master_degree in enumerate(masters_degrees):
            master_str = f"master_degree_{index + 1};{master_degree.department}"
            master_degrees_dict["masters"][master_str] = master_degree.department

        print("master_degrees_dict: ", master_degrees_dict)

        secondary_value = secondary_map.get(result.secondary) if result else None
        higher_value = higher_map.get(result.higher) if result else None
        undergraduation_value = (
            undergraduation_map.get(result.undergraduation) if result else None
        )

        if result.secondary == 1:
            secondary_exam_type = "SSC"

        elif result.secondary == 2:
            secondary_exam_type = "O level"

        elif result.secondary == 3:
            secondary_exam_type = "Dhakhil"

        else:
            higher_exam_type = "N/A"

        if result.higher == 1:
            higher_exam_type = "HSC"

        elif result.higher == 2:
            higher_exam_type = "A level"

        elif result.higher == 3:
            higher_exam_type = "Vocational"

        elif result.higher == 4:
            higher_exam_type = "Diploma"

        else:
            higher_exam_type = "N/A"

        # student result starts
        # Secondary education data
        education_data = []

        secondary_data = {
            "level": secondary_exam_type,
            "institute_name": "N/A",
            "board": result.secondary_board,
            "result": result.secondary_result,
            "roll_no": result.secondary_roll_no if result.secondary_roll_no else "N/A",
            "reg_no": result.secondary_reg_no if result.secondary_reg_no else "N/A",
            "certificate_no": result.secondary_certificate_no
            if result.secondary_certificate_no
            else "N/A",
            "passing_year": result.secondary_passing_year
            if result.secondary_passing_year
            else "N/A",
            "certificate_copy": result.secondary_certificate_copy.url
            if result.secondary_certificate_copy
            else "N/A",
            "created_at": result.created_at if result.created_at else "N/A",
            "updated_at": result.updated_at if result.updated_at else "N/A",
            "verification_status": result.secondary_verification_status,
            "result_id": result.id,
        }
        education_data.append(secondary_data)

        # Higher education data
        higher_data = {
            "level": higher_exam_type,
            "institute_name": "N/A",
            "board": result.higher_board,
            "result": result.higher_result,
            "roll_no": result.higher_roll_no if result.higher_roll_no else "N/A",
            "reg_no": result.higher_reg_no if result.higher_reg_no else "N/A",
            "certificate_no": result.higher_certificate_no
            if result.higher_certificate_no
            else "N/A",
            "passing_year": result.higher_passing_year
            if result.higher_passing_year
            else "N/A",
            "certificate_copy": result.higher_certificate_copy.url
            if result.higher_certificate_copy
            else "N/A",
            "created_at": result.created_at if result.created_at else "N/A",
            "updated_at": result.updated_at if result.updated_at else "N/A",
            "verification_status": result.higher_verification_status,
            "result_id": result.id,
        }
        education_data.append(higher_data)

        # Undergraduate education data
        undergraduate_data = {
            "level": "Undergraduate",
            "institute_name": result.university_name
            if result.university_name
            else "N/A",
            "board": result.undergraduation_board,
            "result": result.undergraduation_result,
            "roll_no": "N/A",
            "reg_no": "N/A",
            "certificate_no": "N/A",
            "passing_year": result.undergraduation_passing_year
            if result.undergraduation_passing_year
            else "N/A",
            "certificate_copy": result.undergraduation_certificate_copy.url
            if result.undergraduation_certificate_copy
            else "N/A",
            "created_at": result.created_at if result.created_at else "N/A",
            "updated_at": result.updated_at if result.updated_at else "N/A",
            "result_id": result.id,
        }

        education_data.append(undergraduate_data)

        # Masters degree
        if masters_degrees.exists():
            for master in masters_degrees:
                masters_data = {
                    "level": f"Masters: {master.department}",
                    "institute_name": master.university if master.university else "N/A",
                    "board": "UGC",
                    "result": master.result if master.result else "N/A",
                    "roll_no": "N/A",
                    "reg_no": "N/A",
                    "certificate_no": "N/A",
                    "passing_year": master.passing_year
                    if master.passing_year
                    else "N/A",
                    "certificate_copy": master.certificate_copy.url
                    if master.certificate_copy
                    else "N/A",
                    "result_id": master.id,
                    "created_at": result.created_at if result.created_at else "N/A",
                    "updated_at": result.updated_at if result.updated_at else "N/A",
                }

                education_data.append(masters_data)

        # Other Certifications/Courses
        if other_certifications.exists():
            for course in other_certifications:
                course_data = {
                    "level": course.course_name.name,
                    "institute_name": course.institute if course.institute else "N/A",
                    "board": "UGC",
                    "result": course.result if course.result else "N/A",
                    "roll_no": "N/A",
                    "reg_no": "N/A",
                    "certificate_no": "N/A",
                    "passing_year": course.passing_year
                    if course.passing_year
                    else "N/A",
                    "certificate_copy": course.certificate_copy.url
                    if course.certificate_copy
                    else "N/A",
                    "result_id": course.id,
                    "created_at": course.created_at if course.created_at else "N/A",
                    "updated_at": course.updated_at if course.updated_at else "N/A",
                }

                education_data.append(course_data)

        # student result ends

        student_details = {
            "id": student.id,
            "full_name": student.full_name,
            "email": student.email,
            "phone": student.phone,
            "address": student.address,
            "status": student.status,
            "created_at": student.created_at.strftime("%Y-%m-%d %H:%M:%S"),
            # 'results': results_data,
        }

        return JsonResponse(
            {
                "student_details": student_details,
                "secondary_value": secondary_value,
                "higher_value": higher_value,
                "undergraduation_value": undergraduation_value,
                "master_degrees_dict": master_degrees_dict,
                "education_data": education_data,
            }
        )

    except Students.DoesNotExist:
        return JsonResponse({"error": "Student not found"}, status=404)


@login_required
@root_required
def consultant_credit_balance(request):
    if request.method == "POST":
        consultant_id = request.POST.get("consultant_id")
        payment_method = request.POST.get("payment_method")
        payment_status = request.POST.get("payment_status")
        reference = request.POST.get("reference")
        amount = request.POST.get("amount")
        amount = amount.replace(",", "")

        try:
            balance = Balances.objects.create(
                acc_pay_to=consultant_id,
                pay_method=payment_method,
                payment_status=payment_status,
                acc_pay_ref=reference,
                acc_credit=amount,
                acc_deal_type=1,
                created_at=datetime.now(),
                updated_at=datetime.now(),
            )

            messages.success(request, "Credit balance added successfully.")
        except Exception as e:
            messages.error(request, f"Error: {e}")

        return redirect("consultant_credit_balance")

    consultants = Users.objects.filter(user_role=5)

    payment_method_choices = Balances._meta.get_field("pay_method").choices
    payment_status_choices = Balances._meta.get_field("payment_status").choices

    context = {
        "consultants": consultants,
        "payment_method_choices": payment_method_choices,
        "payment_status_choices": payment_status_choices,
    }
    return render(request, "roottemplates/consultant_credit_balance.html", context)


@login_required
@root_required
def get_consultant_balance(request):
    if request.method == "GET":
        consultant_id = request.GET.get("consultant_id")
        try:
            total_credit = (
                Balances.objects.filter(acc_pay_to=consultant_id).aggregate(
                    total_credit=Sum("acc_credit")
                )["total_credit"]
                or 0
            )
            total_debit = (
                Balances.objects.filter(acc_paid_by=consultant_id).aggregate(
                    total_debit=Sum("acc_debit")
                )["total_debit"]
                or 0
            )
            balance = total_credit - total_debit
            return JsonResponse({"balance": balance})
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)
    return JsonResponse({}, status=400)


@login_required
@root_required
def get_last_transactions(request):
    if request.method == "GET":
        consultant_id = request.GET.get("consultant_id")
        try:
            # Retrieve both credit and debit transactions for the consultant
            transactions = Balances.objects.filter(
                Q(acc_pay_to=consultant_id) & (Q(acc_credit__gt=0) | Q(acc_debit__gt=0))
            ).order_by("-created_at")[:5]

            transaction_list = [
                {
                    "date": transaction.created_at.strftime(
                        "%Y-%m-%d %H:%M:%S"
                    ),  # Format date as string
                    "reference": transaction.acc_pay_ref,
                    "amount": transaction.acc_credit
                    if transaction.acc_credit
                    else -transaction.acc_debit,  # Use credit if available, else use debit
                    "type": "Credit"
                    if transaction.acc_credit
                    else "Debit",  # Identify transaction type
                }
                for transaction in transactions
            ]
            return JsonResponse({"transactions": transaction_list})
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)
    return JsonResponse({}, status=400)


@login_required
@root_required
def consultant_rates(request):
    # Retrieve all consultants
    consultants = Users.objects.filter(
        user_role=5
    )  # Assuming user_role=5 corresponds to consultants

    # Pass the consultants to the template
    context = {"consultants": consultants}
    return render(request, "roottemplates/consultant_rates.html", context)


@login_required
@root_required
def get_existing_rates(request, consultant_id):
    print("rate consultant id---: ", consultant_id)
    existing_rates = Rates.objects.filter(rate_added_to=consultant_id).first()
    print("existing_rates: ", existing_rates)
    if existing_rates:
        print("got existing rates")
        return JsonResponse(
            {
                "success": True,
                "existing_rates": {
                    "first_rate": existing_rates.first_rate,
                    "second_rate": existing_rates.second_rate,
                    "third_rate": existing_rates.third_rate,
                    "four_rate": existing_rates.four_rate,
                    "five_rate": existing_rates.five_rate,
                },
            }
        )

    else:
        print("no existing rate")
        return JsonResponse(
            {"success": False, "message": "No existing rates for the given consultant."}
        )


@login_required
@root_required
def add_or_update_rates(request, consultant_id):
    if request.method == "POST":
        # Retrieve the consultant
        consultant = get_object_or_404(Users, id=consultant_id)

        # Retrieve rate data from the POST request
        first_rate = request.POST.get("first_rate")
        second_rate = request.POST.get("second_rate")
        third_rate = request.POST.get("third_rate")
        four_rate = request.POST.get("four_rate")
        five_rate = request.POST.get("five_rate")

        # Get existing rates
        existing_rates = Rates.objects.filter(rate_added_to=consultant_id)

        # If rates are already added, update them
        if existing_rates.exists():
            existing_rates = existing_rates.first()
            existing_rates.first_rate = first_rate
            existing_rates.second_rate = second_rate
            existing_rates.third_rate = third_rate
            existing_rates.four_rate = four_rate
            existing_rates.five_rate = five_rate
            existing_rates.save()
        else:
            # If rates are not added, create a new record
            Rates.objects.create(
                rate_added_by=request.user.id,
                rate_added_to=consultant.id,
                first_rate=first_rate,
                second_rate=second_rate,
                third_rate=third_rate,
                four_rate=four_rate,
                five_rate=five_rate,
            )

        # Return a JsonResponse with success message
        return JsonResponse(
            {"success": True, "message": "Rates added/updated successfully."}
        )


@login_required
@root_required
def add_address(request):
    # Ensure the user is Root (user_type 0)
    if request.user.user_type == 0:
        existing_address = Addresses.objects.first()
        existing_map = Maps.objects.first()

        if request.method == "POST":
            office_name = request.POST.get("office_name")
            address = request.POST.get("address")
            hotline = request.POST.get("hotline")
            phone = request.POST.get("phone")
            email = request.POST.get("email")
            map_location = request.POST.get(
                "map_location"
            )  # Assuming you have a form field for map location

            # If an existing address exists, update it with the new details
            if existing_address:
                existing_address.office_name = office_name
                existing_address.address = address
                existing_address.hotline = hotline
                existing_address.phone = phone
                existing_address.email = email
                existing_address.save()
                messages.success(request, "Address updated successfully!")
            else:
                # If no address exists, create a new one
                new_address = Addresses.objects.create(
                    consultant_id=None,  # Set to None as it's not associated with a specific user
                    office_name=office_name,
                    address=address,
                    hotline=hotline,
                    phone=phone,
                    email=email,
                )
                messages.success(request, "Address added successfully!")

            # Update or create map location
            if existing_map:
                existing_map.map_location = map_location
                existing_map.save()
                messages.success(request, "Map location updated successfully!")
            else:
                Maps.objects.create(
                    consultant_id=None,  # Set to None as it's not associated with a specific user
                    map_location=map_location,
                )
                messages.success(request, "Map location added successfully!")

            return redirect("add_address")

        return render(
            request,
            "roottemplates/add_address.html",
            {"existing_address": existing_address, "existing_map": existing_map},
        )


@login_required
@root_required
def process_explenation_root(request):
    # Check if there is an existing Explanation instance
    instance = Explanation.objects.first()

    if request.method == "POST":
        user_id = request.user.id  # Get the id of the current user
        exp_title = request.POST.get("exp_title")
        exp_des = request.POST.get("exp_des")
        exp_img = request.FILES.get("exp_img")  # Use request.FILES for file uploads

        if instance:  # Update operation
            instance.exp_title = exp_title
            instance.exp_des = exp_des
            if exp_img:
                # Delete existing image file
                if instance.exp_img:
                    existing_img_path = os.path.join(
                        settings.MEDIA_ROOT, instance.exp_img.name
                    )
                    if os.path.exists(existing_img_path):
                        os.remove(existing_img_path)
                instance.exp_img = exp_img
                # Construct the image filename
                filename = f"{user_id}-{slugify(instance.exp_title)}{os.path.splitext(exp_img.name)[1]}"
                instance.exp_img.name = os.path.join("explanation", filename)
            instance.updated_at = timezone.now()
            operation_type = "updated"
        else:  # Create operation
            instance = Explanation(
                root_id=user_id,
                exp_title=exp_title,
                exp_des=exp_des,
                created_at=timezone.now(),
                updated_at=timezone.now(),
            )
            if exp_img:
                # Construct the image filename
                filename = f"{user_id}-{slugify(instance.exp_title)}{os.path.splitext(exp_img.name)[1]}"
                instance.exp_img.name = os.path.join("explanation", filename)
            operation_type = "created"

        # Delete the previous image if it exists
        folder_path = os.path.join(settings.MEDIA_ROOT, "explanation")
        previous_img_path = instance.exp_img.path if instance.exp_img else None
        if previous_img_path and os.path.exists(previous_img_path):
            os.remove(previous_img_path)

        instance.save()

        messages.success(request, f"Explanation {operation_type} successfully.")

    return render(request, "roottemplates/process.html", {"instance": instance})


@login_required
@root_required
def client_list(request):
    clients = Clients.objects.all()
    return render(request, "roottemplates/client_list.html", {"clients": clients})


@login_required
def add_client(request):
    if request.method == "POST":
        root_id = request.user.id
        client_image = request.FILES.get("client_image")
        client_name = request.POST.get("client_name")
        client_url = request.POST.get("client_url")

        try:
            client_instance = Clients.objects.create(
                root_id=root_id,
                client_image=client_image,
                client_name=client_name,
                client_url=client_url,
            )
            messages.success(request, "Client added successfully.")
            return redirect(
                "client_list"
            )  # Redirect to the client list page after adding client
        except Exception as e:
            messages.error(request, f"Error adding client: {e}")
            # Handle the error appropriately, for example, return to the same page with an error message
            return redirect("add_client")

    return render(request, "roottemplates/add_client.html")


@login_required
def update_client(request, client_id):
    client_instance = get_object_or_404(Clients, id=client_id)

    if request.method == "POST":
        client_image = request.FILES.get("client_image")
        client_name = request.POST.get("client_name")
        client_url = request.POST.get("client_url")

        try:
            client_instance.client_name = client_name

            if client_url:
                client_instance.client_url = client_url

            if client_image:
                client_instance.client_image = client_image
            client_instance.updated_at = timezone.now()
            client_instance.save()
            messages.success(request, "Client updated successfully.")
            return JsonResponse(
                {"success": True, "message": "Client updated successfully"}
            )
        except Exception as e:
            messages.error(request, f"Error updating client: {e}")
            return JsonResponse({"success": False, "error": str(e)}, status=400)

    return JsonResponse(
        {"success": False, "error": "Invalid request method"}, status=405
    )


@login_required
def delete_client(request, client_id):
    client_instance = get_object_or_404(Clients, id=client_id)

    try:
        client_instance.delete()
        messages.success(request, "Client deleted successfully.")
        return JsonResponse({"success": True})
    except Exception as e:
        messages.error(request, f"Error deleting client: {e}")
        return JsonResponse({"success": False, "error": str(e)}, status=400)


@login_required
@root_required
def save_benefit_for_consultant(request):
    # Retrieve existing Customizes instance for the current user (consultant)
    user = request.user
    instance = Customizes.objects.filter(consultant=user).first()

    if user.is_authenticated and user.user_type == 0:
        if request.method == "POST":
            benefit_list = request.POST.getlist("benefit_list[]")

            if instance:
                # If an instance exists, update its benefit field
                instance.benefit = ", ".join(benefit_list)
                instance.updated_at = timezone.now()
                operation_type = "updated"

            else:
                # If no instance exists, create a new one with status=0
                with transaction.atomic():
                    instance = Customizes.objects.create(
                        consultant=user,
                        benefit=", ".join(benefit_list),
                        status=0,  # Set status to 0
                        created_at=timezone.now(),
                        updated_at=timezone.now(),
                    )
                    operation_type = "created"

            instance.save()

            messages.success(request, f"Benefit {operation_type} successfully.")

    else:
        messages.error(request, f"Not authorized to create Benefit")

    if instance and instance.benefit:
        instance_benefit = instance.benefit.split(",")
    else:
        instance_benefit = []

    print("instance_benefit: ", instance_benefit)

    return render(
        request, "roottemplates/benefit.html", {"benefit_list": instance_benefit}
    )


def check_phone_exist(request):
    if request.method == "POST":
        phone_number = request.POST.get("phone")

        # Check if the phone number exists in User model
        user_exists = Users.objects.filter(phone=phone_number).exists()

        # Return JSON response indicating if phone number exists in any of the models
        return JsonResponse({"exists": user_exists})
    else:
        return JsonResponse({"error": "Invalid request method"}, status=400)


@login_required
def check_email_exist(request):
    if request.method == "POST":
        email = request.POST.get("email")

        # Check if the email exists in User model
        user_exists = Users.objects.filter(email=email).exists()

        # Return JSON response indicating if email exists in any of the models
        return JsonResponse({"exists": user_exists})
    else:
        return JsonResponse({"error": "Invalid request method"}, status=400)


@login_required
def get_all_consultants(request):
    try:
        # Filter users based on user_role
        consultants = Users.objects.filter(user_role=5, active_status__in=[1, 3, 4, 5])
        consultant_data = []
        for consultant in consultants:
            consultant_credits = (
                Balances.objects.filter(acc_pay_to=consultant.id).aggregate(
                    Sum("acc_credit")
                )["acc_credit__sum"]
                or 0.0
            )
            consultant_debits = (
                Balances.objects.filter(acc_paid_by=consultant.id).aggregate(
                    Sum("acc_debit")
                )["acc_debit__sum"]
                or 0.0
            )

            consultant_balance = consultant_credits - consultant_debits
            consultant_details = ConsultantDetails.objects.filter(
                consultant_id=consultant.id
            ).first()
            consultant_data.append(
                {
                    "id": consultant.id,
                    "full_name": consultant.full_name,
                    "email": consultant.email,
                    "phone": consultant.phone,
                    "company_name": consultant.company_name,
                    "establishment_date": consultant.est_date.strftime("%B %d, %Y")
                    if consultant.est_date
                    else None,
                    "balance": consultant_balance,
                    "experience": consultant_details.experience
                    if consultant_details
                    else None,
                    "consultant_img": consultant_details.consultant_img.url
                    if consultant_details and consultant_details.consultant_img
                    else None,
                    # Add other fields as needed
                }
            )
        return JsonResponse({"consultants": consultant_data})
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


@login_required
@root_required
def balance_list(request):
    # Retrieve both credit and debit transactions
    credit_transactions = Balances.objects.filter(acc_credit__isnull=False)
    debit_transactions = Balances.objects.filter(acc_debit__isnull=False)

    for transaction in credit_transactions:
        consultant = Users.objects.filter(id=transaction.acc_pay_to).first()
        transaction.consultant_name = consultant.company_name if consultant else None

    for transaction in debit_transactions:
        consultant = Users.objects.filter(id=transaction.acc_paid_by).first()
        transaction.consultant_name = consultant.company_name if consultant else None

    return render(
        request,
        "roottemplates/balance_list.html",
        {
            "credit_transactions": credit_transactions,
            "debit_transactions": debit_transactions,
        },
    )


@login_required
@root_required
def consultant_wise_scholarship_list(request):
    instances = ConsultantWises.objects.all()
    for instance in instances:
        user = Users.objects.get(id=instance.scow_consultant_id)
        instance.full_name = user.full_name  # Add the full name to the instance
    return render(
        request,
        "roottemplates/consultant_wise_scholarship_list.html",
        {"instances": instances},
    )


@login_required
@permission_required(("visa.change_scholarships",))
def edit_consultant_wise_scholarship(request, scow_id):
    instance = get_object_or_404(ConsultantWises, scow_id=scow_id)
    countries = Countries.objects.all().values(
        "country_id", "country_name"
    )  # Adjusted to use 'country_id'
    if request.method == "POST":
        scow_text = request.POST.get("scow_text")
        scow_whocanapply = request.POST.get("scow_whocanapply")
        scow_status = request.POST.get("scow_status")
        country_id = request.POST.get(
            "country_id"
        )  # Get the selected country ID from the form

        # Fetch the country instance
        country_instance = get_object_or_404(
            Countries, country_id=country_id
        )  # Adjusted to use 'country_id'

        instance.scow_text = scow_text
        instance.scow_whocanapply = scow_whocanapply
        instance.scow_status = scow_status
        instance.country_name = country_instance  # Set the country instance
        instance.updated_at = timezone.now()

        instance.save()
        messages.success(request, "Consultant Wise Scholarship updated successfully.")
        return JsonResponse({"success": True})
    elif request.method == "GET":  # Handle GET request for fetching data
        # Serialize the data to include country name
        data = {
            "scow_text": instance.scow_text,
            "scow_whocanapply": instance.scow_whocanapply,
            "scow_status": instance.scow_status,
            "country_id": instance.country_name.country_id
            if instance.country_name
            else None,  # Send country ID instead of country name
            "countries": list(countries),
        }
        return JsonResponse(data)
    else:
        return JsonResponse(
            {"success": False, "message": "Method Not Allowed"}, status=405
        )


@login_required
@require_POST
def delete_consultant_wise_scholarship(request, scow_id):
    instance = get_object_or_404(ConsultantWises, scow_id=scow_id)
    instance.delete()

    return JsonResponse(
        {
            "success": True,
            "message": "Scholarship deleted successfully",
            "scow_id": scow_id,
        }
    )


@permission_required(("visa.change_scholarships",))
def consutlant_upload(request):
    # Retrieve all uploaded scholarships ordered by the most recent first
    uploaded_scholarships = ScholarShips.objects.all().order_by("-created_at")

    # Iterate through each uploaded scholarship to fetch the consultant's full name
    for scholarship in uploaded_scholarships:
        user = Users.objects.get(id=scholarship.consultant_id)
        scholarship.company_name = user.company_name

    # Pass the uploaded scholarships to the template context
    context = {"uploaded_scholarships": uploaded_scholarships}

    # Render the template with the context
    return render(request, "roottemplates/consultant_upload_scholarship.html", context)


from django.urls import reverse


@permission_required(("visa.change_scholarships",))
def approve_scholarship(request):
    if request.method == "POST":
        try:
            # Retrieve data from the POST request
            scholarship_id = request.POST.get("scholarship_id")
            expiration_time_str = request.POST.get("expiration_time")

            # Retrieve the scholarship object
            scholarship = ScholarShips.objects.get(id=scholarship_id)

            # Update scholarship status
            # Assuming 1 represents approved status

            # Update expiration time if provided
            if expiration_time_str:
                expiration_time = datetime.strptime(expiration_time_str, "%Y-%m-%d")
                scholarship.expiration_time = expiration_time

            # Save the changes
            scholarship.status = 1
            scholarship.save()

            # Display success message
            messages.success(request, "Scholarship approved successfully.")
        except ScholarShips.DoesNotExist:
            messages.error(request, "Scholarship does not exist.")
        except ValueError:
            messages.error(request, "Invalid expiration time format.")

    # Redirect back to the consultant upload page
    return HttpResponseRedirect(reverse("consutlant_upload"))


@permission_required(("visa.change_scholarships",))
def view_scholarship(request, scholarship_id):
    if request.method == "GET":
        scholarship = get_object_or_404(ScholarShips, pk=scholarship_id)
        scholarship_data = {
            "id": scholarship.id,
            "description": scholarship.schp_description,
            "apply_process": scholarship.apply_process,
            "consultant_id": scholarship.consultant_id,
            "created_at": scholarship.created_at.strftime("%Y-%m-%d %H:%M:%S"),
            "updated_at": scholarship.updated_at.strftime("%Y-%m-%d %H:%M:%S")
            if scholarship.updated_at
            else None,
        }
        return JsonResponse({"scholarship": scholarship_data})
    else:
        return JsonResponse({"error": "Method not allowed"}, status=405)


@login_required
@require_POST
@permission_required(("visa.change_scholarships",))
def delete_scholarship_uploaded(request, scholarship_id):
    scholarship = get_object_or_404(ScholarShips, pk=scholarship_id)
    scholarship.delete()

    return JsonResponse(
        {
            "success": True,
            "message": "Scholarship deleted successfully",
            "scholarship_id": scholarship_id,
        }
    )


def course_list(request):
    courses = CourseName.objects.all()
    return render(request, "roottemplates/course_list.html", {"courses": courses})


def add_course(request):
    if request.method == "POST":
        course_name = request.POST.get("course_name")
        if course_name:
            CourseName.objects.create(name=course_name)
            return redirect("course_list")
    return render(request, "roottemplates/add_course.html")


def edit_course(request, course_id):
    course = get_object_or_404(CourseName, pk=course_id)
    if request.method == "POST":
        new_course_name = request.POST.get("new_course_name")
        if new_course_name:
            course.name = new_course_name
            course.save()
            return JsonResponse(
                {"success": True, "message": "Course updated successfully"}
            )
        else:
            return JsonResponse(
                {"success": False, "message": "New course name cannot be empty"}
            )
    else:
        return JsonResponse({"success": False, "message": "Invalid request method"})


def delete_course(request, course_id):
    course = get_object_or_404(CourseName, pk=course_id)
    if request.method == "POST":
        course.delete()
        return JsonResponse({"success": True, "message": "Course deleted successfully"})
    return JsonResponse({"success": False, "message": "Invalid request"})


def add_visa_service(request):
    if request.method == "POST":
        # এখানে ফর্ম সেভ করার লজিক হবে
        title = request.POST.get("title")
        subtitle = request.POST.get("subtitle")
        image = request.FILES.get("image")
        short_desc = request.POST.get("short_description")
        content = request.POST.get("content")
        VisaService.objects.create(
            title=title,
            subtitle=subtitle,
            image=image,
            short_description=short_desc,
            content=content,
        )
        return redirect("manage_visa_services")
    return render(request, "roottemplates/add_service.html")


def manage_visa_services(request):
    services = VisaService.objects.all()
    return render(request, "roottemplates/manage_services.html", {"services": services})

# from django.shortcuts import render, get_object_or_404, redirect
# from django.contrib import messages
# from .models import SelfFundedProgram, University, Countries


# def manage_self_funded_programs(request):
#     if request.method == 'POST':
#         try:
#             country_id = request.POST.get('country_id')
#             university_id = request.POST.get('university_id')
#             semester_fee = request.POST.get('semester_fee')
#             requirements = request.POST.get('requirements')
#             foreign_student_policy = request.POST.get('foreign_student_policy')

#             if not all([country_id, university_id, semester_fee, requirements, foreign_student_policy]):
#                 messages.error(request, 'All fields are required.')
#                 return redirect('manage_self_funded_programs')

#             country = get_object_or_404(Countries, country_id=country_id) # country_id
#             university = get_object_or_404(University, university_id=university_id) # university_id

#             SelfFundedProgram.objects.create(
#                 country=country,
#                 university=university,
#                 semester_fee=semester_fee,
#                 requirements=requirements,
#                 foreign_student_policy=foreign_student_policy,
#             )
#             messages.success(request, 'Self Funded Program added successfully.')
#             return redirect('manage_self_funded_programs')

#         except Exception as e:
#             messages.error(request, f'Something went wrong: {str(e)}')
#             return redirect('manage_self_funded_programs')

#     programs = SelfFundedProgram.objects.select_related('university', 'country').all()
#     countries = Countries.objects.all().order_by('country_name')
#     universities = University.objects.select_related('countries').all()

#     context = {
#         'programs': programs,
#         'countries': countries,
#         'universities': universities,
#     }
    
#     return render(request, 'roottemplates/manage_self_funded.html', context)


def delete_self_funded_program(request, program_id):
    program = get_object_or_404(SelfFundedProgram, id=program_id)
    try:
        program.delete()
        messages.success(request, 'Program deleted successfully.')
    except Exception as e:
        messages.error(request, f'Could not delete program: {str(e)}')
    return redirect('roottemplates/manage_self_funded_programs')

# def get_universities_by_country(request):
#     country_id = request.GET.get('country_id')
#     if country_id:
#         universities = University.objects.filter(country_id=country_id).values('id', 'name')
#         return JsonResponse({'universities': list(universities)})
#     return JsonResponse({'universities': []})

# from .models import University, Countries
# from django.shortcuts import render, redirect
# from django.contrib import messages

# def manage_universities(request):
#     if request.method == "POST":
#         name = request.POST.get('name')
#         country_id = request.POST.get('country')
#         logo = request.FILES.get('logo')
        
#         if name and country_id:
#             country = Countries.objects.get(country_id=country_id)
#             University.objects.create(name=name, country=country, university_logo=logo)
#             messages.success(request, "University added successfully!")
#             return redirect('manage_universities')

#     universities = University.objects.all().order_by('-created_at')
#     countries = Countries.objects.all().order_by('country_name')
    
#     return render(request, 'roottemplates/manage_universities.html', {
#         'universities': universities,
#         'countries': countries
#     }) 
    
# from .models import University, Countries
# from django.shortcuts import render, redirect
# from django.contrib import messages

# def manage_universities(request):
#     if request.method == "POST":
#         name = request.POST.get('name')
#         country_id = request.POST.get('country_id') 
        
#         if name and country_id:
            
#             University.objects.create(name=name, countries_id=country_id)
#             messages.success(request, "University added successfully!")
#             return redirect('manage_universities')

#     universities = University.objects.all().order_by('-created_at')
#     countries = Countries.objects.all().order_by('country_name') 
    
#     return render(request, 'roottemplates/manage_universities.html', {
#         'universities': universities,
#         'countries': countries
#     })
@login_required
@require_POST
# def delete_university(request, uni_id):
#     uni = get_object_or_404(University, id=uni_id)
#     uni.delete()
#     messages.success(request, "University deleted!")
#     return redirect('manage_universities')
def delete_university(request, uni_id):
    uni = get_object_or_404(University, university_id=uni_id) # মডেলের প্রাইমারি কি 'university_id'
    uni.delete()
    messages.success(request, f"'{uni.name}' has been deleted!")
    return redirect('manage_universities')
    




# ---------------------------------------------------------------------------
# HELPER — build the absolute flag URL safely
# ---------------------------------------------------------------------------
def _flag_url(request, country):
    """
    Returns the public URL for a country's flag, or None.
    Works whether country_flag is a Django ImageField/FileField or a plain
    CharField storing a relative path.
    """
    flag = country.country_flag
    if not flag:
        return None
    # ImageField / FileField — has a .url property
    if hasattr(flag, 'url'):
        try:
            return request.build_absolute_uri(flag.url)
        except Exception:
            return None
    # Plain CharField storing e.g. "flags/us.png"
    from django.conf import settings
    return request.build_absolute_uri(
        settings.MEDIA_URL + str(flag).lstrip('/')
    )


# ---------------------------------------------------------------------------
# Manage Universities
# ---------------------------------------------------------------------------
@login_required
# def manage_universities(request):
#     """
#     Add / delete universities.
#     University.countries is the FK field name pointing to the Countries model.
#     """
#     countries    = Countries.objects.all().order_by('country_name')
#     universities = University.objects.select_related('countries').order_by('name')

#     if request.method == 'POST':
#         action = request.POST.get('action')

#         if action == 'add':
#             name       = request.POST.get('name', '').strip()
#             country_id = request.POST.get('country_id')
#             if name and country_id:
#                 country = get_object_or_404(Countries, country_id=country_id)
#                 University.objects.create(name=name, countries=country)
#                 messages.success(request, f'University "{name}" added successfully.')
#             else:
#                 messages.error(request, 'Please provide both a university name and a country.')

#         elif action == 'delete':
#             university_id = request.POST.get('university_id')
#             uni = get_object_or_404(University, university_id=university_id)
#             uni_name = uni.name
#             uni.delete()
#             messages.success(request, f'University "{uni_name}" deleted.')

#         return redirect('manage_universities')

#     context = {
#         'countries':    countries,
#         'universities': universities,
#     }
#     return render(request, 'roottemplates/manage_universities.html', context)
def manage_universities(request):
    if request.method == "POST":
        name = request.POST.get('name')
        country_id = request.POST.get('country_id')
        
        if name and country_id:
            try:
               
                University.objects.create(name=name, country_id=country_id)
                messages.success(request, f"'{name}' has been added successfully!")
            except Exception as e:
                messages.error(request, f"Could not save university. Error: {e}")
            return redirect('manage_universities')

    universities = University.objects.select_related('country').all().order_by('-created_at')
    countries = Countries.objects.all().order_by('country_name') 
    
    return render(request, 'roottemplates/manage_universities.html', {
        'universities': universities,
        'countries': countries
    })


# ---------------------------------------------------------------------------
# AJAX — get universities filtered by country
# ---------------------------------------------------------------------------
# def get_universities_by_country(request):
#     """
#     GET /ajax/universities/?country_id=<id>
#     Returns JSON list: [{"id": 1, "name": "..."}, ...]
#     University FK to Countries uses field name `countries`.
#     """
#     country_id = request.GET.get('country_id', '').strip()

#     if not country_id:
#         return JsonResponse({'error': 'country_id is required.'}, status=400)

#     try:
#         universities = (
#             University.objects
#             .filter(countries__country_id=country_id)
#             .order_by('name')
#             .values('university_id', 'name')
#         )
#         data = [
#             {'id': u['university_id'], 'name': u['name']}
#             for u in universities
#         ]
#         return JsonResponse(data, safe=False)
#     except Exception as e:
#         return JsonResponse({'error': str(e)}, status=500)

# def get_universities_by_country(request):
#     country_id = request.GET.get('country_id')
#     if country_id:
       
#        universities = University.objects.filter(countries__country_id=country_id).values('university_id', 'name')
#     return JsonResponse({'universities': list(universities)})
#     return JsonResponse({'universities': []})

def get_universities_by_country(request):
    country_id = request.GET.get('country_id')
    if country_id:
        # 🎯 P0 Fix: 'countries__country_id' এর বদলে সরাসরি 'country_id' (কারণ মডেলে FK-র নাম country)
        universities = University.objects.filter(country_id=country_id).values('university_id', 'name')
        return JsonResponse({'universities': list(universities)})
    return JsonResponse({'universities':[]})

# ---------------------------------------------------------------------------
# Manage Self-Funded Programs
# ---------------------------------------------------------------------------
@login_required
# def manage_self_funded_programs(request):
#     """
#     Add / delete self-funded programs.
#     SelfFundedProgram has:
#       - country    → FK to Countries  (field name: country)
#       - university → FK to University (field name: university)
#     """
#     countries = Countries.objects.all().order_by('country_name')
#     programs  = (
#         SelfFundedProgram.objects
#         .select_related('country', 'university')
#         .order_by('country__country_name', 'university__name')
#     )

#     if request.method == 'POST':
#         action = request.POST.get('action')

#         if action == 'add':
#             country_id    = request.POST.get('country_id')
#             university_id = request.POST.get('university_id')
#             semester_fee  = request.POST.get('semester_fee', '').strip()
#             requirements  = request.POST.get('requirements', '').strip()
#             foreign_policy = request.POST.get('foreign_student_policy', '').strip()

#             if country_id and university_id:
#                 country    = get_object_or_404(Countries,  country_id=country_id)
#                 university = get_object_or_404(University, university_id=university_id)
#                 SelfFundedProgram.objects.create(
#                     country=country,
#                     university=university,
#                     semester_fee=semester_fee,
#                     requirements=requirements,
#                     foreign_student_policy=foreign_policy,
#                 )
#                 messages.success(
#                     request,
#                     f'Self-Funded program for "{university.name}" added successfully.'
#                 )
#             else:
#                 messages.error(request, 'Please select both a country and a university.')

#         elif action == 'delete':
#             program_id = request.POST.get('program_id')
#             program = get_object_or_404(SelfFundedProgram, id=program_id)
#             uni_name = program.university.name
#             program.delete()
#             messages.success(request, f'Program for "{uni_name}" deleted.')

#         return redirect('manage_self_funded_programs')

#     context = {
#         'countries': countries,
#         'programs':  programs,
#     }
#     return render(request, 'roottemplates/manage_self_funded.html', context)


def manage_self_funded_programs(request):
    if request.method == 'POST':
        # 🎯 P0 Fix: ডিফল্টভাবে 'add' ধরে নিবে, যাতে hidden action না থাকলেও সেভ হয়
        action = request.POST.get('action', 'add')

        if action == 'add':
            country_id = request.POST.get('country_id')
            university_id = request.POST.get('university_id')
            semester_fee = request.POST.get('semester_fee')
            requirements = request.POST.get('requirements')
            foreign_student_policy = request.POST.get('foreign_student_policy')

            if not all([country_id, university_id, semester_fee, requirements, foreign_student_policy]):
                messages.error(request, 'All fields are required.')
                return redirect('manage_self_funded_programs')

            country = get_object_or_404(Countries, country_id=country_id)
            university = get_object_or_404(University, university_id=university_id)

            # 🎯 P2 Fix: Cross-validation (যাতে হ্যাক করে অন্য দেশের ভার্সিটি সেভ করতে না পারে)
            if university.country_id != country.country_id:
                messages.error(request, 'Security Error: University does not belong to the selected country.')
                return redirect('manage_self_funded_programs')

            SelfFundedProgram.objects.create(
                country=country,
                university=university,
                semester_fee=semester_fee,
                requirements=requirements,
                foreign_student_policy=foreign_student_policy,
            )
            messages.success(request, f'Self Funded Program for {university.name} added successfully.')
            return redirect('manage_self_funded_programs')

        elif action == 'delete':
            program_id = request.POST.get('program_id')
            program = get_object_or_404(SelfFundedProgram, id=program_id)
            program.delete()
            messages.success(request, 'Program deleted successfully.')
            return redirect('manage_self_funded_programs')

    # GET Request
    programs = SelfFundedProgram.objects.select_related('university', 'country').all()
    countries = Countries.objects.all().order_by('country_name')

    context = {
        'programs': programs,
        'countries': countries,
    }
    return render(request, 'roottemplates/manage_self_funded.html', context)


from .models import ScholarshipStep

@login_required
def manage_procedure(request):
    if request.method == "POST":
        action = request.POST.get('action')
        
        if action == "add":
            country_id = request.POST.get('country_id')
            step_number = request.POST.get('step_number')
            title = request.POST.get('title')
            description = request.POST.get('description')
            
            if country_id and step_number and title:
                try:
                    country = get_object_or_404(Countries, country_id=country_id)
                    ScholarshipStep.objects.create(
                        country=country,
                        step_number=int(step_number),
                        title=title,
                        description=description
                    )
                    messages.success(request, f"Step '{title}' added successfully!")
                except Exception as e:
                    messages.error(request, f"Error saving step: {e}")
            else:
                messages.error(request, "Please fill in all required fields.")
            return redirect('manage_procedure')

        elif action == "delete":
            step_id = request.POST.get('step_id')
            step = get_object_or_404(ScholarshipStep, id=step_id)
            step.delete()
            messages.success(request, "Step deleted successfully.")
            return redirect('manage_procedure')

    countries = Countries.objects.all().order_by('country_name')
    # Use select_related to prevent N+1 DB queries
    procedures = ScholarshipStep.objects.select_related('country').all().order_by('country__country_name', 'step_number')

    return render(request, 'roottemplates/manage_procedure.html', {
        'countries': countries,
        'procedures': procedures
    })


@login_required
@root_required
def manage_seo_settings(request):
    fixed_site_name = "Student Visa BD"
    global_seo, _ = SEOSettings.objects.get_or_create(
        id=1,
        defaults={
            "site_name": fixed_site_name,
            "meta_title": "",
            "meta_description": "",
            "meta_keywords": "",
            "asset_version": "1.0",
        },
    )

    if global_seo.site_name != fixed_site_name:
        global_seo.site_name = fixed_site_name
        global_seo.save()

    selected_page_key = request.GET.get("page_key", "global")
    page_choices = [
        {"value": "global", "label": "Global Defaults"}
    ] + [
        {"value": value, "label": label}
        for value, label in PageSEOSettings.PAGE_CHOICES
    ]

    page_seo = None
    seo_settings = global_seo

    if selected_page_key != "global":
        page_seo, _ = PageSEOSettings.objects.get_or_create(
            page_key=selected_page_key,
            defaults={
                "site_name": fixed_site_name,
            },
        )
        if page_seo.site_name != fixed_site_name:
            page_seo.site_name = fixed_site_name
            page_seo.save()
        seo_settings = page_seo

    keyword_pool = MetaKeywordPool.objects.order_by("word")

    def normalize_keywords(raw_keywords):
        normalized = []
        seen = set()

        for keyword in raw_keywords:
            clean_keyword = keyword.strip().lower()
            if clean_keyword and clean_keyword not in seen:
                seen.add(clean_keyword)
                normalized.append(clean_keyword)

        return normalized

    if request.method == "POST":
        selected_page_key = request.POST.get("page_key", "global")
        seo_settings = global_seo

        if selected_page_key != "global":
            seo_settings, _ = PageSEOSettings.objects.get_or_create(
                page_key=selected_page_key,
                defaults={"site_name": fixed_site_name},
            )

        seo_settings.site_name = fixed_site_name
        seo_settings.meta_title = request.POST.get("meta_title", "")
        seo_settings.meta_description = request.POST.get("meta_description", "")
        seo_settings.google_verification_id = request.POST.get(
            "google_verification_id", ""
        )
        seo_settings.analytics_code = request.POST.get("analytics_code", "")
        seo_settings.asset_version = request.POST.get(
            "asset_version", seo_settings.asset_version
        )

        submitted_keywords = request.POST.getlist("meta_keywords")
        if not submitted_keywords:
            submitted_keywords = request.POST.get("meta_keywords", "").split(",")

        new_keywords = request.POST.get("new_keywords", "").split(",")

        normalized_keywords = normalize_keywords(submitted_keywords + new_keywords)
        seo_settings.meta_keywords = ", ".join(normalized_keywords)

        for keyword in normalized_keywords:
            MetaKeywordPool.objects.get_or_create(word=keyword)

        og_image = request.FILES.get("og_image")
        if og_image:
            seo_settings.og_image = og_image

        seo_settings.save()
        selected_page_label = dict(PageSEOSettings.PAGE_CHOICES).get(
            selected_page_key,
            "Global Defaults",
        )
        if selected_page_key == "global":
            selected_page_label = "Global Defaults"

        messages.success(
            request,
            f"SEO Settings updated successfully for {selected_page_label}.",
        )
        return redirect(f"{reverse('manage_seo_settings')}?page_key={selected_page_key}")

    return render(
        request,
        "roottemplates/manage_seo.html",
        {
            "global_seo": global_seo,
            "seo_settings": seo_settings,
            "selected_page_key": selected_page_key,
            "selected_page_label": (
                "Global Defaults"
                if selected_page_key == "global"
                else dict(PageSEOSettings.PAGE_CHOICES).get(
                    selected_page_key,
                    "Selected Page",
                )
            ),
            "page_choices": page_choices,
            "keyword_pool": keyword_pool,
            "selected_keywords": [
                keyword.strip()
                for keyword in seo_settings.meta_keywords.split(",")
                if keyword.strip()
            ],
            "keyword_options": sorted(
                {
                    keyword.word for keyword in keyword_pool
                }.union(
                    {
                        keyword.strip()
                        for keyword in seo_settings.meta_keywords.split(",")
                        if keyword.strip()
                    }
                )
            ),
        },
    )


@login_required
@root_required
def view_seo_settings(request):
    global_seo = SEOSettings.objects.first()
    page_seo_settings = PageSEOSettings.objects.order_by("page_key")

    return render(
        request,
        "roottemplates/view_seo.html",
        {
            "global_seo": global_seo,
            "page_seo_settings": page_seo_settings,
            "page_choice_map": dict(PageSEOSettings.PAGE_CHOICES),
        },
    )
