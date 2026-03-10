from django.shortcuts import render
from django.views.generic import DetailView
from .models import *
from django.contrib.auth import authenticate, login, logout
from .emailBackend import EmailBackend
from django.shortcuts import redirect
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.contrib import messages
import re, random, requests
from datetime import datetime, timedelta
from django.core.serializers import serialize
from django.urls import reverse, resolve
from .serializers import ThanaSerializer
from django.utils.safestring import mark_safe
from django.shortcuts import render, get_object_or_404
import json
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.hashers import make_password
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import F, Case, When, Value, IntegerField
from time import time
from django.http import Http404

from django.core.mail import send_mail
from django.conf import settings
from django.views.decorators.http import require_POST
from requests.exceptions import Timeout, ConnectionError
from requests.adapters import HTTPAdapter
from urllib3.util import Retry
from django.contrib.auth.hashers import check_password
from django.core.exceptions import ObjectDoesNotExist
from django.core.files.storage import default_storage
from .models import CustomUser
from django.db.models import Q


def home(request):
    # if user.user_type == 0:
    # if Customizes.objects.exists():
    #     customize = Customizes.objects.last()

    # else:
    #     customize = ''

    root_users = CustomUser.objects.filter(user_type=0)
    customize = Customizes.objects.filter(consultant__in=root_users).first()

    clients = Clients.objects.all()
    process_explanation = Explanation.objects.order_by("-id").first()
    page_name = "Home"
    page_description = "'This is a top level student visa related information web portal, you can get any types of information from here. also you can take lates of visa agent information from here.'"
    page_keywords = "'education visa consultant agent in dhaka, student visa informatin agent, student visa need, student visa consultant company, need student visa from dhaka,'"

    print("customize: ", customize)

    top_consultants = Users.objects.filter(user_role=5).order_by("-rating")[:4]

    consultant_details = []
    for consultant in top_consultants:
        details = ConsultantDetails.objects.filter(consultant_id=consultant.id).first()
        consultant_details.append(details)

    visa_services = VisaService.objects.filter(is_active=True)

    context = {
        "top_consultants": zip(top_consultants, consultant_details),
        "customize": customize,
        "process_explanation": process_explanation,
        "clients": clients,
        "page_name": page_name,
        "page_description": page_description,
        "page_keywords": page_keywords,
        "visa_services": visa_services,
    }

    return render(request, "index.html", context)


def signup_user(request):
    districts = District.objects.all().order_by("name")
    signup_type = "consultant"

    thanas = Thana.objects.filter(district_id=1)

    page_name = "signup user"
    page_description = "'This is a top level student visa related information web portal, you can get any types of information from here. also you can take lates of visa agent information from here.'"
    page_keywords = "'education visa consultant agent in dhaka, student visa informatin agent, student visa need, student visa consultant company, need student visa from dhaka,'"

    context = {
        "districts": districts,
        "signup_type": signup_type,
        "page_name": page_name,
        "page_description": page_description,
        "page_keywords": page_keywords,
    }

    return render(request, "user_login/signup_user.html", context)


def signup_student(request):
    districts = District.objects.all().order_by("name")
    countries = Countries.objects.all()
    signup_type = "student"
    page_name = "signup student"
    page_description = "'This is a top level student visa related information web portal, you can get any types of information from here. also you can take lates of visa agent information from here.'"
    page_keywords = "'education visa consultant agent in dhaka, student visa informatin agent, student visa need, student visa consultant company, need student visa from dhaka,'"

    context = {
        "districts": districts,
        "countries": countries,
        "signup_type": signup_type,
        "page_name": page_name,
        "page_description": page_description,
        "page_keywords": page_keywords,
    }
    return render(request, "user_login/signup_student.html", context)


def redirect_to_otp(request):
    if request.method == "POST":
        # captcha_token = request.POST.get("g-recaptcha-response")
        # cap_url = "https://www.google.com/recaptcha/api/siteverify"
        # cap_secret = "6LcxvG8pAAAAAIaMvcT9M_ys9A7ytKR1UCIZFvKW"
        # cap_data = {"secret": cap_secret, "response": captcha_token}
        # cap_server_response = requests.post(url=cap_url, data=cap_data)
        # cap_json = json.loads(cap_server_response.text)

        # if not cap_json.get('success', False):
        #     return JsonResponse({'errors': 'Invalid Captcha. Try Again.'})
        cap_json = {"success": True}
        # else
        signup_type = request.POST.get("signup_type")

        # print('signup_type: ', signup_type)

        if signup_type == "consultant":
            company_name = request.POST.get("company_name")
            phone = request.POST.get("phone")
            email = request.POST.get("email")
            full_name = request.POST.get("owner_name")
            district_id = request.POST.get("district_name")
            thana_id = request.POST.get("thana_name")
            address = request.POST.get("office_address")
            password = request.POST.get("password")
            confirm_password = request.POST.get("confirm_password")

            if (
                company_name
                and phone
                and email
                and full_name
                and district_id
                and thana_id
                and address
                and password
                and confirm_password
            ):
                if password == confirm_password:
                    consultant_phone = Users.objects.filter(phone=phone).first()
                    user_phone = CustomUser.objects.filter(
                        phone=phone, user_type=1
                    ).first()
                    consultant_email = Users.objects.filter(email=email).first()
                    user_email = CustomUser.objects.filter(
                        email=email, user_type=1
                    ).first()
                    valid_phone_number = re.match(
                        r"^(013|014|015|016|017|018|019)\d{8}$", phone
                    )

                    if consultant_phone is None and user_phone is None:
                        if consultant_email is None and user_email is None:
                            if valid_phone_number:
                                temp_user_data = {
                                    "full_name": full_name,
                                    "company_name": company_name,
                                    "email": email,
                                    "phone": phone,
                                    "district_id": district_id,
                                    "thana_id": thana_id,
                                    "address": address,
                                    "password": password,
                                    "signup_type": signup_type,
                                }

                                otp = "".join(
                                    random.choice("0123456789") for _ in range(6)
                                )
                                expiration_time = int(time()) + 300
                                temp_user_data["expiration_time"] = expiration_time
                                temp_user_data["otp"] = otp
                                request.session["temp_user_data"] = temp_user_data

                                url = f"http://sms.iglweb.com/api/v1/send?api_key=44517101314545131710131454&contacts=88{phone}&senderid=01844532638&msg={otp} is your activation code in Student Visa Bd.This code will expire in 2 Hours.For help,call:01958666999"

                                retry_strategy = Retry(
                                    total=4,
                                    status_forcelist=[429, 500, 502, 503, 504],
                                )
                                adapter = HTTPAdapter(max_retries=retry_strategy)

                                session = requests.Session()
                                session.mount("http://", adapter)
                                session.mount("https://", adapter)

                                try:
                                    response = session.get(url)
                                    print("SMS API Response:", response.text)
                                    if response.status_code == 200:
                                        return JsonResponse(
                                            {
                                                "success": True,
                                                "redirect_url": "/otp_verification_signup/",
                                                "expiration_time": expiration_time,
                                            }
                                        )
                                    else:
                                        return JsonResponse(
                                            {
                                                "errors": f"Server returned status code {response.status_code}. Please try again later."
                                            }
                                        )

                                except Timeout:
                                    return JsonResponse(
                                        {
                                            "errors": "Request timed out. Please try again later."
                                        }
                                    )

                                except ConnectionError:
                                    return JsonResponse(
                                        {
                                            "errors": "Failed to establish connection to the server. Please check your internet connection and try again later."
                                        }
                                    )

                                # except requests.exceptions.RequestException as e:
                                #     return JsonResponse({'errors': f'An error occurred: {str(e)}'})

                            else:
                                return JsonResponse({"errors": "Invalid phone number"})
                        else:
                            return JsonResponse(
                                {"errors": "A user with this email already exists"}
                            )
                    else:
                        return JsonResponse(
                            {"errors": "A user with this phone already exists"}
                        )

                else:
                    return JsonResponse({"errors": "Passwords do not match"})
            else:
                return JsonResponse(
                    {"errors": "Please fill up all the required fields"}
                )

        elif signup_type == "student":
            full_name = request.POST.get("full_name")
            email = request.POST.get("email")
            phone = request.POST.get("phone")
            user_type = request.POST.get("user_type")
            gender = request.POST.get("gender")
            address = request.POST.get("address")
            district_id = request.POST.get("district_name")
            thana_id = request.POST.get("thana_name")
            countries = request.POST.get("countries")
            password = request.POST.get("password")
            confirm_password = request.POST.get("confirm_password")
            countries_json = json.loads(request.POST["countries"])

            if (
                full_name
                and email
                and phone
                and user_type
                and gender
                and address
                and district_id
                and thana_id
                and countries
                and password
                and confirm_password
            ):
                if password == confirm_password:
                    consultant_phone = Students.objects.filter(phone=phone).first()
                    consultant_email = Students.objects.filter(email=email).first()
                    valid_phone_number = re.match(
                        r"^(013|019|018|014|015|016|017)\d{8}$", phone
                    )

                    if consultant_phone is None:
                        if consultant_email is None:
                            if valid_phone_number:
                                temp_user_data = {
                                    "full_name": full_name,
                                    "email": email,
                                    "phone": phone,
                                    "user_type": user_type,
                                    "gender": gender,
                                    "district_id": district_id,
                                    "thana_id": thana_id,
                                    "address": address,
                                    "countries": countries_json,
                                    "password": password,
                                    "signup_type": signup_type,
                                }

                                otp = "".join(
                                    random.choice("0123456789") for _ in range(6)
                                )
                                expiration_time = int(time()) + 300
                                temp_user_data["expiration_time"] = expiration_time
                                temp_user_data["otp"] = otp
                                request.session["temp_user_data"] = temp_user_data
                                url = f"http://sms.iglweb.com/api/v1/send?api_key=44517101314545131710131454&contacts=88{phone}&senderid=01844532638&msg={otp} is your activation code in Student Visa Bd.This code will expire in 2 Hours.For help,call:01958666999"

                                retry_strategy = Retry(
                                    total=4,
                                    status_forcelist=[429, 500, 502, 503, 504],
                                )
                                adapter = HTTPAdapter(max_retries=retry_strategy)

                                session = requests.Session()
                                session.mount("http://", adapter)
                                session.mount("https://", adapter)

                                try:
                                    response = session.get(url)
                                    print("SMS API Response:", response.text)
                                    # response = requests.get(url)
                                    if response.status_code == 200:
                                        return JsonResponse(
                                            {
                                                "success": True,
                                                "redirect_url": "/otp_verification_signup_student/",
                                                "expiration_time": expiration_time,
                                            }
                                        )
                                    else:
                                        return JsonResponse(
                                            {
                                                "errors": f"Server returned status code {response.status_code}. Please try again later."
                                            }
                                        )

                                except Timeout:
                                    return JsonResponse(
                                        {
                                            "errors": "Request timed out. Please try again later."
                                        }
                                    )

                                except ConnectionError:
                                    return JsonResponse(
                                        {
                                            "errors": "Failed to establish connection to the server. Please check your internet connection and try again later."
                                        }
                                    )

                                except requests.exceptions.RequestException as e:
                                    return JsonResponse(
                                        {"errors": f"An error occurred: {str(e)}"}
                                    )

                            else:
                                return JsonResponse({"errors": "Invalid phone number"})
                        else:
                            return JsonResponse(
                                {"errors": "A user with this email already exists"}
                            )
                    else:
                        return JsonResponse(
                            {"errors": "A user with this phone already exists"}
                        )

                else:
                    return JsonResponse({"errors": "Passwords do not match"})
            else:
                return JsonResponse(
                    {"errors": "Please fill up all the required fields"}
                )

        else:
            return JsonResponse({"errors": "Invalid signup type"})


def otp_verification_signup(request):
    temp_user_data = request.session.get("temp_user_data")
    time_remaining = temp_user_data["expiration_time"]

    page_name = "OTP Verification Consultant"
    page_description = "'This is a top level student visa related information web portal, you can get any types of information from here. also you can take lates of visa agent information from here.'"
    page_keywords = "'education visa consultant agent in dhaka, student visa informatin agent, student visa need, student visa consultant company, need student visa from dhaka,'"

    if request.method == "GET":
        resend_otp = request.GET.get("resend", "")

        if resend_otp and resend_otp == "true":
            if request.session["temp_user_data"]:
                previous_expiration_time = request.session["temp_user_data"][
                    "expiration_time"
                ]
                previous_otp = request.session["temp_user_data"]["otp"]

                previous_expiration_datetime = timezone.make_aware(
                    datetime.utcfromtimestamp(previous_expiration_time),
                    timezone=timezone.utc,
                )

                if (
                    previous_expiration_time
                    and timezone.now() > previous_expiration_datetime
                ):
                    # Clear session data if expiration time has passed
                    del request.session["temp_user_data"]["otp"]
                    del request.session["temp_user_data"]["expiration_time"]

                    phone = request.session["temp_user_data"]["phone"]
                    valid_phone_number = request.session["temp_user_data"]["phone"]
                    otp = str(random.randint(1000, 9999))
                    url = f"http://sms.iglweb.com/api/v1/send?api_key=44517101314545131710131454&contacts=88{phone}&senderid=01844532638&msg={otp} is your activation code in Student Visa Bd.This code will expire in 2 Hours.For help,call:01958666999"
                    response = requests.get(url)
                    expiration_time_resend = int(time()) + 300
                    request.session["temp_user_data"]["otp"] = otp
                    request.session["temp_user_data"]["expiration_time"] = (
                        expiration_time_resend
                    )
                    request.session.modified = True  # Mark session as modified

                    response_data = {
                        "success": True,
                        "redirect_url": "/forgot_password_otp_verification/",
                        "otp": otp,
                        "expiration_time": expiration_time_resend,  # Send expiration time to client
                    }

                    response = JsonResponse(response_data)

                    return response
            else:
                return JsonResponse({"error": "Please Retry"})

    phone_number = request.session["temp_user_data"]["phone"]

    return render(
        request,
        "user_login/otp_verification_signup.html",
        {
            "expiration_time": time_remaining,
            "phone": phone_number,
            "page_name": page_name,
            "page_description": page_description,
            "page_keywords": page_keywords,
        },
    )


def otp_verification_signup_student(request):
    temp_user_data = request.session.get("temp_user_data")
    time_remaining = temp_user_data["expiration_time"]

    countries = temp_user_data["countries"]
    countries_str = ", ".join(countries)

    page_name = "OTP Verification Student"
    page_description = "'This is a top level student visa related information web portal, you can get any types of information from here. also you can take lates of visa agent information from here.'"
    page_keywords = "'education visa consultant agent in dhaka, student visa informatin agent, student visa need, student visa consultant company, need student visa from dhaka,'"

    if request.method == "GET":
        resend_otp = request.GET.get("resend", "")

        if resend_otp and resend_otp == "true":
            if request.session["temp_user_data"]:
                previous_expiration_time = request.session["temp_user_data"][
                    "expiration_time"
                ]
                previous_otp = request.session["temp_user_data"]["otp"]

                previous_expiration_datetime = timezone.make_aware(
                    datetime.utcfromtimestamp(previous_expiration_time),
                    timezone=timezone.utc,
                )

                if (
                    previous_expiration_time
                    and timezone.now() > previous_expiration_datetime
                ):
                    # Clear session data if expiration time has passed
                    del request.session["temp_user_data"]["otp"]
                    del request.session["temp_user_data"]["expiration_time"]

                    phone = request.session["temp_user_data"]["phone"]
                    valid_phone_number = request.session["temp_user_data"]["phone"]
                    otp = str(random.randint(1000, 9999))
                    url = f"http://sms.iglweb.com/api/v1/send?api_key=44517101314545131710131454&contacts=88{phone}&senderid=01844532638&msg={otp} is your activation code in Student Visa Bd.This code will expire in 2 Hours.For help,call:01958666999"
                    response = requests.get(url)
                    expiration_time_resend = int(time()) + 300
                    request.session["temp_user_data"]["otp"] = otp
                    request.session["temp_user_data"]["expiration_time"] = (
                        expiration_time_resend
                    )
                    request.session.modified = True  # Mark session as modified

                    response_data = {
                        "success": True,
                        "redirect_url": "/forgot_password_otp_verification/",
                        "otp": otp,
                        "expiration_time": expiration_time_resend,  # Send expiration time to client
                    }

                    response = JsonResponse(response_data)

                    return response
            else:
                return JsonResponse({"error": "Please Retry"})

    phone_number = request.session["temp_user_data"]["phone"]

    return render(
        request,
        "user_login/otp_verification_signup_student.html",
        {
            "expiration_time": time_remaining,
            "phone": phone_number,
            "page_name": page_name,
            "page_description": page_description,
            "page_keywords": page_keywords,
        },
    )


def change_number(request):
    if request.method == "GET":
        phone = request.GET["phone"]

        print("phone number sent: ", phone)

        if phone:
            valid_phone_number = re.match(
                r"^(013|019|018|014|015|016|017)\d{8}$", phone
            )

            signup_type = request.session["temp_user_data"]["signup_type"]
            consultant_user = CustomUser.objects.filter(
                phone=phone, user_type=1
            ).first()
            student_user = CustomUser.objects.filter(phone=phone, user_type=2).first()

            if signup_type == "student" and student_user is None:
                user = Students.objects.filter(phone=phone).first()

            elif signup_type == "student" and student_user:
                user = student_user

            if signup_type == "consultant" and consultant_user is None:
                user = Users.objects.filter(phone=phone).first()

            elif signup_type == "consultant" and consultant_user:
                user = consultant_user

            if user is None:
                if valid_phone_number:
                    expiration_time = int(time()) + 300
                    otp = str(random.randint(100000, 999999))
                    request.session["temp_user_data"]["otp"] = otp
                    request.session["temp_user_data"]["expiration_time"] = (
                        expiration_time
                    )
                    request.session["temp_user_data"]["phone"] = phone
                    request.session.modified = True
                    changed_phone = request.session["temp_user_data"]["phone"]
                    url = f"http://sms.iglweb.com/api/v1/send?api_key=44517101314545131710131454&contacts=88{phone}&senderid=01844532638&msg={otp} is your activation code in Student Visa Bd.This code will expire in 2 Hours.For help,call:01958666999"
                    response = requests.get(url)
                    print("SMS API Response:", response.text)

                    if response.status_code == 200:
                        return JsonResponse(
                            {
                                "success": True,
                                "redirect_url": "/otp_verification_signup_student/",
                                "expiration_time": expiration_time,
                                "changed_phone": changed_phone,
                            }
                        )
            else:
                return JsonResponse({"error": "Phone number already exists"})


def forgot_password_phone_or_email(request):
    if request.method == "POST":
        phone = request.POST.get("phone")

        if phone:
            consultant = Users.objects.filter(phone=phone).first()

            if consultant is not None:
                otp = str(random.randint(1000, 9999))

                valid_phone_number = re.match(
                    r"^(013|019|018|014|015|016|017)\d{8}$", str(phone)
                )
                temp_user_data = {"phone": phone, "otp": otp}

                if valid_phone_number:
                    url = f"http://sms.iglweb.com/api/v1/send?api_key=44517101314545131710131454&contacts=88{phone}&senderid=01844532638&msg={otp} is your activation code in Student Visa Bd.This code will expire in 2 Hours.For help,call:01958666999"
                    response = requests.get(url)
                    if response.status_code == 200:
                        response = JsonResponse(
                            {
                                "success": True,
                                "redirect_url": "/forgot_password_otp_verification/",
                            }
                        )
                        expiration_time = int(time()) + 300
                        temp_user_data["expiration_time"] = expiration_time
                        request.session["temp_user_data"] = temp_user_data

                        response_data = {
                            "success": True,
                            "redirect_url": "/forgot_password_otp_verification/",
                            "expiration_time": expiration_time,  # Send expiration time to client
                        }

                        response = JsonResponse(response_data)

                        return response

                else:
                    return JsonResponse({"error": "Invalid Phone Number Provided"})

            else:
                return JsonResponse({"error": "Phone Number is not registered"})

    return render(request, "user_login/forgot_password_phone_or_email.html")


def forgot_password_otp_verification(request):
    temp_data = request.session["temp_user_data"]
    time_remaining = temp_data["expiration_time"]
    page_name = "Forgot Password Otp Verification"
    page_description = "'This is a top level student visa related information web portal, you can get any types of information from here. also you can take lates of visa agent information from here.'"
    page_keywords = "'education visa consultant agent in dhaka, student visa informatin agent, student visa need, student visa consultant company, need student visa from dhaka,'"

    if request.method == "GET":
        resend_otp = request.GET.get("resend", "")

        if resend_otp and resend_otp == "true":
            if request.session["temp_user_data"]:
                previous_expiration_time = request.session["temp_user_data"][
                    "expiration_time"
                ]
                previous_otp = request.session["temp_user_data"]["otp"]

                previous_expiration_datetime = timezone.make_aware(
                    datetime.utcfromtimestamp(previous_expiration_time),
                    timezone=timezone.utc,
                )

                if (
                    previous_expiration_time
                    and timezone.now() > previous_expiration_datetime
                ):
                    # Clear session data if expiration time has passed
                    del request.session["temp_user_data"]["otp"]
                    del request.session["temp_user_data"]["expiration_time"]

                    phone = request.session["temp_user_data"]["phone"]
                    valid_phone_number = request.session["temp_user_data"]["phone"]
                    otp = str(random.randint(1000, 9999))
                    url = f"http://sms.iglweb.com/api/v1/send?api_key=44517101314545131710131454&contacts=88{phone}&senderid=01844532638&msg={otp} is your activation code in Student Visa Bd.This code will expire in 2 Hours.For help,call:01958666999"
                    response = requests.get(url)
                    expiration_time_resend = int(time()) + 300
                    request.session["temp_user_data"]["otp"] = otp
                    request.session["temp_user_data"]["expiration_time"] = (
                        expiration_time_resend
                    )
                    request.session.modified = True  # Mark session as modified

                    response_data = {
                        "success": True,
                        "redirect_url": "/forgot_password_otp_verification/",
                        "otp": otp,
                        "expiration_time": expiration_time_resend,  # Send expiration time to client
                    }

                    response = JsonResponse(response_data)

                    return response
            else:
                return JsonResponse({"error": "Please Retry"})

    elif request.method == "POST":
        stored_otp = request.session["temp_user_data"]["otp"]
        entered_otp = request.POST.get("otp")

        if entered_otp == stored_otp:
            return JsonResponse(
                {"success": True, "redirect_url": "/change_forgotten_password/"}
            )

        else:
            return JsonResponse({"errors": "Invalid OTP"})

    return render(
        request,
        "user_login/forgot_password_otp_verification.html",
        {
            "expiration_time": time_remaining,
            "page_name": page_name,
            "page_description": page_description,
            "page_keywords": page_keywords,
        },
    )


def change_forgotten_password(request):
    temp_data = request.session.get("temp_user_data")

    page_name = "change forgotten password"
    page_description = "'This is a top level student visa related information web portal, you can get any types of information from here. also you can take lates of visa agent information from here.'"
    page_keywords = "'education visa consultant agent in dhaka, student visa informatin agent, student visa need, student visa consultant company, need student visa from dhaka,'"

    if request.method == "POST":
        phone = temp_data["phone"]
        new_password = request.POST.get("password")
        confirm_password = request.POST.get("confirm_password")

        if new_password and confirm_password:
            if new_password == confirm_password:
                consultant = Users.objects.filter(phone=phone).first()
                if consultant:
                    user = CustomUser.objects.filter(id=consultant.id).first()

                    if user:
                        user.set_password(new_password)
                        consultant.raw_password = new_password
                        consultant.password = make_password(new_password)
                        user.save()
                        consultant.save()

                        return JsonResponse({"success": True})

                    else:
                        return JsonResponse(
                            {"errors": "Your account hasn't been approved yet"}
                        )

                else:
                    return JsonResponse({"errors": "Phone Number is not Registered"})

            else:
                return JsonResponse({"errors": "Passwords do not match"})

        else:
            return JsonResponse({"errors": "Please fill up all the requuired fields"})

    return render(
        request,
        "user_login/change_forgotten_password.html",
        {
            "page_name": page_name,
            "page_description": page_description,
            "page_keywords": page_keywords,
        },
    )


def forgot_password_phone_or_email_student(request):
    page_name = "forgot_password_phone_or_email_student"
    page_description = "'This is a top level student visa related information web portal, you can get any types of information from here. also you can take lates of visa agent information from here.'"
    page_keywords = "'education visa consultant agent in dhaka, student visa informatin agent, student visa need, student visa consultant company, need student visa from dhaka,'"
    if request.method == "POST":
        phone = request.POST.get("phone")

        if phone:
            student = Students.objects.filter(phone=phone).first()

            if student is not None:
                otp = str(random.randint(1000, 9999))

                valid_phone_number = re.match(
                    r"^(013|019|018|014|015|016|017)\d{8}$", str(phone)
                )
                temp_user_data = {"phone": phone, "otp": otp}

                if valid_phone_number:
                    url = f"http://sms.iglweb.com/api/v1/send?api_key=44517101314545131710131454&contacts=88{phone}&senderid=01844532638&msg={otp} is your activation code in Student Visa Bd.This code will expire in 2 Hours.For help,call:01958666999"
                    response = requests.get(url)
                    if response.status_code == 200:
                        response = JsonResponse(
                            {
                                "success": True,
                                "redirect_url": "/forgot_password_otp_verification_student/",
                            }
                        )
                        expiration_time = int(time()) + 300
                        temp_user_data["expiration_time"] = expiration_time
                        request.session["temp_user_data"] = temp_user_data

                        response_data = {
                            "success": True,
                            "redirect_url": "/forgot_password_otp_verification_student/",
                            "expiration_time": expiration_time,  # Send expiration time to client
                        }

                        json_response = JsonResponse(response_data)

                        return json_response
                else:
                    return JsonResponse({"error": "Invalid Phone Number Provided"})

            else:
                return JsonResponse({"error": "Phone Number is not registered"})

    return render(
        request,
        "user_login/forgot_password_phone_or_email_student.html",
        {
            "page_name": page_name,
            "page_description": page_description,
            "page_keywords": page_keywords,
        },
    )


def forgot_password_otp_verification_student(request):
    temp_data = request.session["temp_user_data"]
    time_remaining = temp_data["expiration_time"]
    page_name = "Forgot password otp verification student"
    page_description = "'This is a top level student visa related information web portal, you can get any types of information from here. also you can take lates of visa agent information from here.'"
    page_keywords = "'education visa consultant agent in dhaka, student visa informatin agent, student visa need, student visa consultant company, need student visa from dhaka,'"

    if request.method == "GET":
        resend_otp = request.GET.get("resend", "")

        if resend_otp and resend_otp == "true":
            if request.session["temp_user_data"]:
                previous_expiration_time = request.session["temp_user_data"][
                    "expiration_time"
                ]
                previous_otp = request.session["temp_user_data"]["otp"]

                previous_expiration_datetime = timezone.make_aware(
                    datetime.utcfromtimestamp(previous_expiration_time),
                    timezone=timezone.utc,
                )

                if (
                    previous_expiration_time
                    and timezone.now() > previous_expiration_datetime
                ):
                    # Clear session data if expiration time has passed
                    del request.session["temp_user_data"]["otp"]
                    del request.session["temp_user_data"]["expiration_time"]

                    phone = request.session["temp_user_data"]["phone"]
                    valid_phone_number = request.session["temp_user_data"]["phone"]
                    otp = str(random.randint(1000, 9999))
                    url = f"http://sms.iglweb.com/api/v1/send?api_key=44517101314545131710131454&contacts=88{phone}&senderid=01844532638&msg={otp} is your activation code in Student Visa BD.This code will expire in 2 Hours.For help,call:01958666999"
                    response = requests.get(url)
                    expiration_time_resend = int(time()) + 300
                    request.session["temp_user_data"]["otp"] = otp
                    request.session["temp_user_data"]["expiration_time"] = (
                        expiration_time_resend
                    )
                    request.session.modified = True

                    response_data = {
                        "success": True,
                        "redirect_url": "/forgot_password_otp_verification_student/",
                        "otp": otp,
                        "expiration_time": expiration_time_resend,  # Send expiration time to client
                    }

                    json_response = JsonResponse(response_data)

                    return json_response
            else:
                return JsonResponse({"error": "Please Retry"})

    elif request.method == "POST":
        stored_otp = request.session["temp_user_data"]["otp"]
        entered_otp = request.POST.get("otp")

        if entered_otp == stored_otp:
            return JsonResponse(
                {"success": True, "redirect_url": "/change_forgotten_password_student/"}
            )

        else:
            return JsonResponse({"errors": "Invalid OTP"})

    return render(
        request,
        "user_login/forgot_password_otp_verification_student.html",
        {
            "expiration_time": time_remaining,
            "page_name": page_name,
            "page_description": page_description,
            "page_keywords": page_keywords,
        },
    )


def change_forgotten_password_student(request):
    temp_data = request.session.get("temp_user_data")
    page_name = "Change forgotten password student"
    page_description = "This is a top level student visa related information web portal, you can get any types of information from here. also you can take lates of visa agent information from here."
    page_keywords = "education visa consultant agent in dhaka, student visa informatin agent, student visa need, student visa consultant company, need student visa from dhaka,"
    if request.method == "POST":
        phone = temp_data["phone"]
        new_password = request.POST.get("password")
        confirm_password = request.POST.get("confirm_password")

        if new_password and confirm_password:
            if new_password == confirm_password:
                student = Students.objects.filter(phone=phone).first()
                if student:
                    user = CustomUser.objects.filter(id=student.id).first()

                    if user:
                        user.set_password(new_password)
                        student.raw_password = new_password
                        student.password = make_password(new_password)
                        user.save()
                        student.save()

                        return JsonResponse({"success": True})

                    else:
                        return JsonResponse(
                            {"errors": "Your account hasn't been approved yet"}
                        )

                else:
                    return JsonResponse({"errors": "Phone Number is not Registered"})

            else:
                return JsonResponse({"errors": "Passwords do not match"})

        else:
            return JsonResponse({"errors": "Please fill up all the requuired fields"})

    # else:
    return render(
        request,
        "user_login/change_forgotten_password_student.html",
        {
            "page_name": page_name,
            "page_description": page_description,
            "page_keywords": page_keywords,
        },
    )


def save_user_signup(request):
    if request.method == "POST":
        temp_user_data = request.session.get("temp_user_data")
        entered_otp = request.POST.get("otp")
        stored_otp = temp_user_data["otp"]

        if entered_otp == stored_otp:
            full_name = temp_user_data["full_name"]
            company_name = temp_user_data["company_name"]
            email = temp_user_data["email"]
            phone = temp_user_data["phone"]
            district_id = int(temp_user_data["district_id"])
            thana_id = temp_user_data["thana_id"]
            address = temp_user_data["address"]
            password = temp_user_data["password"]
            expiration_time = temp_user_data["expiration_time"]
            otp = temp_user_data["otp"]

            district = get_object_or_404(District, id=district_id)
            thana = get_object_or_404(Thana, id=thana_id)

            # Create a new user in the Users table
            user = Users.objects.create(
                full_name=full_name,
                company_name=company_name,
                phone=phone,
                email=email,
                district=district,
                thana=thana,
                address=address,
                user_role=5,
                raw_password=password,
                created_at=timezone.now(),
            )

            user.password = make_password(password)
            user.save()

            return JsonResponse({"success": True})
        else:
            return JsonResponse({"error": "Incorrect OTP"})


def save_student_signup(request):
    if request.method == "POST":
        temp_user_data = request.session.get("temp_user_data")
        entered_otp = request.POST.get("otp")
        stored_otp = temp_user_data["otp"]
        if entered_otp == stored_otp:
            full_name = temp_user_data["full_name"]
            email = temp_user_data["email"]
            phone = temp_user_data["phone"]
            user_type = temp_user_data["user_type"]
            gender = temp_user_data["gender"]
            district_id = int(temp_user_data["district_id"])
            thana_id = temp_user_data["thana_id"]
            address = temp_user_data["address"]
            countries = temp_user_data["countries"]
            password = temp_user_data["password"]
            expiration_time = temp_user_data["expiration_time"]
            otp = temp_user_data["otp"]
            country_string = ""
            district = District.objects.get(id=district_id)
            thana = Thana.objects.get(id=thana_id)
            print("district: ", district)
            user = CustomUser.objects.create(
                username=full_name,
                email=email,
                user_type=2,
                phone=phone,
            )
            user.set_password(password)
            user.save()
            student = Students.objects.create(
                id=user.id,
                full_name=full_name,
                email=email,
                phone=phone,
                user_type=user_type,
                gender=gender,
                district=district,
                thana=thana,
                address=address,
                status=1,
                raw_password=password,
                created_at=timezone.now(),
            )

            student_countires = Countries.objects.filter(country_id__in=countries)
            student.countries.add(*student_countires)
            student.password = user.password
            student.save()

            StudentDetails.objects.create(dets_regs_id=user.id, dets_status=1)

            return JsonResponse({"success": True})
        else:
            return JsonResponse({"error": "Incorrect OTP"})


# def login_user(request):
#     page_name = "Login User"
#     page_description = "This is a top level student visa related information web portal, you can get any types of information from here. also you can take lates of visa agent information from here.'"
#     page_keywords = "education visa consultant agent in dhaka, student visa informatin agent, student visa need, student visa consultant company, need student visa from dhaka,"
#     if request.method == "POST":
#         # captcha_token = request.POST.get("g-recaptcha-response")
#         # cap_url = "https://www.google.com/recaptcha/api/siteverify"
#         # cap_secret = "6LcxvG8pAAAAAIaMvcT9M_ys9A7ytKR1UCIZFvKW"
#         # cap_data = {"secret": cap_secret, "response": captcha_token}
#         # cap_server_response = requests.post(url=cap_url, data=cap_data)
#         # cap_json = json.loads(cap_server_response.text)

#         # if cap_json['success'] == False:
#         #     messages.error(request, "Invalid Captcha. Try Again.")
#         #     return redirect("login_user")

#         cap_json = {"success": True}

#         identifier = request.POST.get("identifier")
#         password = request.POST.get("password")

#         if identifier is not None and password is not None:
#             if "@" in identifier:  # Assuming email contains '@'
#                 # user = EmailBackend().authenticate(request, email=identifier, password=password)
#                 root_user = EmailBackend().authenticate(
#                     request, email=identifier, password=password, user_type=0
#                 )
#                 consultant_user = EmailBackend().authenticate(
#                     request, email=identifier, password=password, user_type=1
#                 )

#                 if root_user:
#                     user = root_user
#                 elif consultant_user:
#                     user = consultant_user
#                 else:
#                     user = None

#             else:
#                 # user = EmailBackend().authenticate(request, phone=identifier, password=password)
#                 root_user = EmailBackend().authenticate(
#                     request, phone=identifier, password=password, user_type=0
#                 )
#                 consultant_user = EmailBackend().authenticate(
#                     request, phone=identifier, password=password, user_type=1
#                 )

#                 if root_user:
#                     user = root_user
#                 elif consultant_user:
#                     user = consultant_user
#                 else:
#                     user = None

#             if user is not None and (user.user_type == 0 or user.user_type == 1):
#                 login(request, user)

#                 if user.user_type == 0:
#                     return redirect(
#                         "root_home"
#                     )  # Redirect to admin_home for user_type 0
#                 elif user.user_type == 1:
#                     return redirect(
#                         "consultant_home"
#                     )  # Redirect to consultant_home for user_type 1
#             else:
#                 messages.error(request, "Invalid credentials")
#         else:
#             messages.error(request, "Please provide both identifier and password.")

#     return render(
#         request,
#         "user_login/login_user.html",
#         {
#             "page_name": page_name,
#             "page_description": page_description,
#             "page_keywords": page_keywords,
#         },
#     )

def login_user(request):
    page_name = "Login User"
    page_description = "This is a top level student visa related information web portal..."
    page_keywords = "education visa consultant agent..."
    
    if request.method == "POST":
        identifier = request.POST.get("identifier", "").strip()
        password = request.POST.get("password", "")

        if identifier and password:
            # ১. প্রথমে মেইন (Approved) CustomUser টেবিলে খুঁজবে
            if "@" in identifier:
                user = CustomUser.objects.filter(
                    Q(email__iexact=identifier) | Q(username__iexact=identifier)
                ).first()
            else:
                user = CustomUser.objects.filter(phone=identifier).first()

            if user is not None:
                # মেইন টেবিলে ইউজার আছে, এবার পাসওয়ার্ড চেক
                if user.check_password(password):
                    if str(user.user_type) == '1': # কনসালট্যান্ট
                        is_verified = getattr(user, 'active_status', getattr(user, 'is_active', True))
                        if is_verified: 
                            login(request, user)
                            return redirect("consultant_home")
                        else:
                            messages.warning(request, "Verification Pending: Your account is currently under review by the Admin.")
                            return redirect("login_user")

                    elif str(user.user_type) == '0': # রুট এডমিন
                        login(request, user)
                        return redirect("root_home")
                    else:
                        messages.error(request, "Access Denied. You do not have permission.")
                        return redirect("login_user")
                else:
                    messages.error(request, "Invalid Password. Please try again.")
            
            else:
                # ২. মেইন টেবিলে নেই! এবার পেন্ডিং (Users) টেবিলে খুঁজবে
                if "@" in identifier:
                    pending_user = Users.objects.filter(email__iexact=identifier, user_role=5).first()
                else:
                    pending_user = Users.objects.filter(phone=identifier, user_role=5).first()

                if pending_user:
                    # ইউজার পেন্ডিং টেবিলে পাওয়া গেছে! 
                    messages.warning(request, "Verification Pending: Your account is currently under review by the Admin.")
                    return redirect("login_user")
                else:
                    # কোনো টেবিলেই নেই
                    messages.error(request, "No account found. Please check your spelling.")
                
        else:
            messages.error(request, "Please provide both identifier and password.")

    return render(
        request,
        "user_login/login_user.html",
        {
            "page_name": page_name,
            "page_description": page_description,
            "page_keywords": page_keywords,
        }
    )

def login_student(request):
    base_template = "base.html"
    print("base_template up: ", base_template)
    print("request.GET.get up: ", request.GET.get("next"))
    page_name = "Login Student"
    page_description = "This is a top level student visa related information web portal, you can get any types of information from here. also you can take lates of visa agent information from here."
    page_keywords = "education visa consultant agent in dhaka, student visa informatin agent, student visa need, student visa consultant company, need student visa from dhaka"

    if request.method == "POST":
        # captcha_token = request.POST.get("g-recaptcha-response")
        # cap_url = "https://www.google.com/recaptcha/api/siteverify"
        # cap_secret = "6LcxvG8pAAAAAIaMvcT9M_ys9A7ytKR1UCIZFvKW"
        # cap_data = {"secret": cap_secret, "response": captcha_token}
        # cap_server_response = requests.post(url=cap_url, data=cap_data)
        # cap_json = json.loads(cap_server_response.text)

        # if cap_json['success'] == False:
        #     messages.error(request, "Invalid Captcha. Try Again.")
        #     return redirect("login_student")

        cap_json = {"success": True}

        identifier = request.POST.get(
            "identifier"
        )  # Use 'identifier' for both email and phone
        password = request.POST.get("password")

        # Get the next parameter from the query string (if available)
        # next_page = request.GET.get('next', None)

        if "next_page" in request.session:
            print("has next page")
            next_page = request.session["next_page"]

        else:
            next_page = None

        # Check if the identifier is an email or phone number
        if "@" in identifier:  # Assuming email contains '@'
            user = EmailBackend().authenticate(
                request, email=identifier, password=password, user_type=2
            )
        else:
            user = EmailBackend().authenticate(
                request, phone=identifier, password=password, user_type=2
            )

        if user and user.user_type == 2:
            login(request, user)

            # Redirect to the next_page if available, otherwise go to student_home
            if next_page:
                return redirect(next_page)
            else:
                return redirect("home")
        else:
            messages.error(request, "Invalid credentials")

    # Display a message indicating the need to log in only if next_page is specified
    # if request.GET.get('next'):
    if "next_page" in request.session:
        next_url = request.session["next_page"]
        print("next_url: ", next_url)

        if next_url:
            print("next_url: ", next_url)
            resolved = resolve(next_url)
            view_name = resolved.view_name
            # If there are parameters in the URL, you can access them using resolved.kwargs
            consultant_id = resolved.kwargs.get("consultant_id", None)
            if consultant_id is not None:
                consultant = get_object_or_404(Users, id=consultant_id)
                consultant_details = get_object_or_404(
                    ConsultantDetails, consultant_id=consultant_id
                )
                print("consultant details: ", consultant)

            print("View name:", view_name)
            print("Consultant ID:", consultant_id)

            # in the HTML file extend the desired html base file according to the next
            if view_name == "singel_consultant_review":
                refined_url = f"/{view_name}/consultant_id/"
                base_template = "consultant_base.html"
                print("veiw name matched")

            else:
                refined_url = None
                consultant = None
                base_template = "base.html"

        else:
            base_template = "base.html"

        print("base template: ", base_template)

        context = {
            "next_url": next_url,
            "url_name": view_name,
            "consultant_id": consultant_id,
            "refined_url": refined_url,
            "base_template": base_template,
            "consultant": consultant,
            "page_name": page_name,
            "consultant": consultant,
            "consultant_details": consultant_details,
            "page_description": page_description,
            "page_keywords": page_keywords,
        }
        messages.info(request, "You need to log in first.")

    else:
        print("base_template: ", base_template)

        context = {
            "base_template": base_template,
        }

    return render(request, "user_login/login_user.html", context)


def logout_user(request):
    user_session = UserSession.objects.filter(
        user=request.user, end_time__isnull=True
    ).first()
    if user_session:
        user_session.end_time = timezone.now()
        user_session.save()
    logout(request)
    return redirect("home")  # Redirect to the home page or adjust the URL as needed


def get_thana(request):
    if request.method == "GET" and "district_id" in request.GET:
        district_id = request.GET["district_id"]
        district = District.objects.get(id=district_id)
        print("district_id: ", district_id)

        thanas = district.thanas.all()

        serializer = ThanaSerializer(thanas, many=True)
        thanas = serializer.data

        print("thana serializer: ", thanas)

    return JsonResponse({"success": True, "thanas": thanas}, safe=False)


def contact(request):
    category_choices = (
        Message.CATEGORY_CHOICES
    )  # Retrieve category choices from the Message model
    page_name = "Contact"
    page_description = "This is a top level student visa related information web portal, you can get any types of information from here. also you can take lates of visa agent information from here."
    page_keywords = "education visa consultant agent in dhaka, student visa informatin agent, student visa need, student visa consultant company, need student visa from dhaka,"

    if request.method == "POST":
        # Extract data from the request
        category = request.POST.get("category")
        email = request.POST.get("email")
        name = request.POST.get("name")
        phonenumber = request.POST.get("phonenumber")
        subject = request.POST.get("subject")
        message_text = request.POST.get("message")
        captcha_token = request.POST.get("g-recaptcha-response")

        # Perform reCAPTCHA verification
        cap_url = "https://www.google.com/recaptcha/api/siteverify"
        cap_secret = "6LcxvG8pAAAAAIaMvcT9M_ys9A7ytKR1UCIZFvKW"
        cap_data = {"secret": cap_secret, "response": captcha_token}
        cap_server_response = requests.post(url=cap_url, data=cap_data)
        cap_json = json.loads(cap_server_response.text)

        if cap_json.get("success", False):
            try:
                # Create and save a Message instance
                message = Message.objects.create(
                    category=category,
                    email=email,
                    name=name,
                    phonenumber=phonenumber,
                    subject=subject,
                    message=message_text,
                    created_at=timezone.now(),
                )

                # Send email notification
                email_subject = f"New message received: {subject}"
                email_message = f"Name: {name}\nEmail: {email}\nPhone Number: {phonenumber}\nMessage: {message_text}"
                sender_email = settings.EMAIL_HOST_USER
                recipient_email = (
                    settings.EMAIL_HOST_USER
                )  # Send email to configured email address
                send_mail(email_subject, email_message, sender_email, [recipient_email])

                messages.success(request, "Message submitted successfully!")
            except Exception as e:
                messages.error(request, f"An error occurred: {str(e)}")
            return redirect("contact")
        else:
            messages.error(request, "Please complete the reCAPTCHA verification.")
            return redirect("contact")

    # Fetch consultants with user_type = 0
    consultants = CustomUser.objects.filter(user_type=0)

    # Initialize a list to store consultant maps
    consultant_maps = []

    # Retrieve map locations for each consultant
    for consultant in consultants:
        maps = Maps.objects.filter(consultant_id=consultant.id)
        for map in maps:
            consultant_maps.append(
                {
                    "consultant": consultant,
                    "map_location": map.map_location,  # Corrected field name
                }
            )

    addresses = Addresses.objects.filter(root_id__isnull=False)
    return render(
        request,
        "contact.html",
        {
            "addresses": addresses,
            "category_choices": category_choices,
            "consultant_maps": consultant_maps,
            "page_name": page_name,
            "page_description": page_description,
            "page_keywords": page_keywords,
        },
    )


def process_explanation(request):
    page_name = "Process Explanation"
    page_description = "This is a top level student visa related information web portal, you can get any types of information from here. also you can take lates of visa agent information from here."
    page_keywords = "education visa consultant agent in dhaka, student visa informatin agent, student visa need, student visa consultant company, need student visa from dhaka,"

    explanations = Explanation.objects.all()
    return render(
        request,
        "process_explenation.html",
        {
            "explanations": explanations,
            "page_name": page_name,
            "page_description": page_description,
            "page_keywords": page_keywords,
        },
    )


def consultant_list(request):
    # Retrieve consultants with user_role=5
    users = CustomUser.objects.filter(user_type=1)
    consultants = Users.objects.filter(
        id__in=users.values("id"), active_status__in=[1, 3, 4, 5]
    ).order_by("id")
    fav_consultant_ids = []

    try:
        # Assuming dets_regs_id is the user ID
        student_details = StudentDetails.objects.get(dets_regs_id=request.user.id)

        # Split the comma-separated list of favorite consultant IDs
        if student_details.dets_favconsultantlist:
            fav_consultant_ids = [
                int(id) for id in student_details.dets_favconsultantlist.split(",")
            ]
    except ObjectDoesNotExist:
        # Handle the case where StudentDetails does not exist for the user
        student_details = None

    # Retrieve consultant details
    consultant_details = ConsultantDetails.objects.filter(
        consultant_id__in=consultants
    ).order_by("consultant_id")
    countries = Countries.objects.all()
    page_name = "Consultant List"
    page_description = "This is a top level student visa related information web portal, you can get any types of information from here. also you can take lates of visa agent information from here."
    page_keywords = "education visa consultant agent in dhaka, student visa informatin agent, student visa need, student visa consultant company, need student visa from dhaka,"

    # Initialize page number
    page = request.GET.get("page")

    # Combine consultants and details into a list of dictionaries
    consultants_with_details = [
        {"consultant": consultant, "details": details}
        for consultant, details in zip(consultants, consultant_details)
    ]

    if not page:
        # Shuffle the list of consultants only if pagination is not in use
        seed = int(time())
        random.seed(seed)
        random.shuffle(consultants_with_details)

    # Apply pagination
    paginator = Paginator(consultants_with_details, 15)

    try:
        chunked_consultants = paginator.page(page)
    except PageNotAnInteger:
        chunked_consultants = paginator.page(1)
    except EmptyPage:
        chunked_consultants = paginator.page(paginator.num_pages)

    context = {
        "chunked_consultants": chunked_consultants,
        "page_name": page_name,
        "fav_consultant_ids": fav_consultant_ids,
        "page_description": page_description,
        "page_keywords": page_keywords,
    }

    # Search function
    if request.method == "GET":
        search_input = request.GET.get("search_area") or ""
        rating_filter = request.GET.get("rating_filter") or ""
        country_filter = request.GET.get("country_filter") or ""
        experience_filter = request.GET.get("experience_filter") or ""

        print("rating_filter: ", rating_filter)
        print("country_filter: ", country_filter)
        print("experience_filter: ", experience_filter)

        # queryset = Users.objects.filter(user_role=5)
        queryset = Users.objects.filter(
            id__in=users.values("id"), active_status__in=[1, 3, 4, 5]
        )
        print("queryset in the begining: ", queryset)
        if search_input or rating_filter or country_filter or experience_filter:
            if not rating_filter:
                rating_filter = "high"

            if rating_filter == "high":
                # queryset_user = Users.objects.filter(company_name__icontains=search_input, user_role=5).order_by('-rating')
                queryset_user = Users.objects.filter(
                    company_name__icontains=search_input, active_status__in=[1, 3, 4, 5]
                ).order_by("-rating")
                queryset = list(queryset_user.values_list("id", flat=True))

                consultant_length = len(queryset)

                for user in queryset_user:
                    print("user each filter: ", user)
                    print("user get: ", Users.objects.get(id=user.id))

                print("queryset_user: ", queryset_user)
                print("queryset for rating: ", queryset)
                print("------rating is high------")

            elif rating_filter == "low":
                # queryset_user = Users.objects.filter(company_name__icontains=search_input, user_role=5).order_by('rating')
                queryset_user = Users.objects.filter(
                    company_name__icontains=search_input, active_status__in=[1, 3, 4, 5]
                ).order_by("rating")
                queryset = list(queryset_user.values_list("id", flat=True))
                print("------rating is low------")

            if experience_filter and experience_filter == "high":
                if country_filter:
                    country_id_int = int(country_filter)
                    country = Countries.objects.get(country_id=country_id_int)
                    # consultant_details = ConsultantDetails.objects.filter(consultant_id__in=queryset, consultant_countries__in=[country]).order_by('-experience')

                    ordering_conditions = [
                        When(id=user_id, then=pos)
                        for pos, user_id in enumerate(queryset, start=1)
                    ]
                    consultant_details = ConsultantDetails.objects.filter(
                        consultant_id__in=queryset, consultant_countries__in=[country]
                    ).order_by(Case(*ordering_conditions, default=0))

                    print("consultant_details: ", consultant_details)

                    # user_ordering_conditions = [When(id=user_id, then=pos) for pos, user_id in enumerate(consultant_details, start=1)]
                    # consultant_details_ids = list(consultant_details.values_list('consultant_id', flat=True))
                    # print('consultant_details_ids when experience is high and country is there: ', consultant_details_ids)
                    # consultant_users = Users.objects.filter(id__in=consultant_details_ids).order_by(Case(*user_ordering_conditions, default=0))

                    # user_ordering_conditions = [When(consultant_id=user_id, then=pos) for pos, user_id in enumerate(consultant_details, start=1)]
                    # consultant_details_ids = list(consultant_details.values_list('id', flat=True))
                    # print('consultant_details_ids when experience is high and country is there: ', consultant_details_ids)
                    # consultant_users = Users.objects.filter(id__in=consultant_details_ids).order_by(Case(*user_ordering_conditions, default=0))

                    # # print('consultant_users when experience is high and country is there: ', consultant_users)

                    # queryset = list(consultant_users.values_list('id', flat=True))

                    print(
                        "queryset when the experience is high and country is there: ",
                        queryset,
                    )
                    print("------experience is high and country is there------")

                else:
                    # consultant_details = ConsultantDetails.objects.filter(consultant_id__in=queryset).order_by('experience')
                    ordering_conditions = [
                        When(consultant_id=user_id, then=pos)
                        for pos, user_id in enumerate(queryset, start=1)
                    ]
                    consultant_details = ConsultantDetails.objects.filter(
                        consultant_id__in=queryset
                    ).order_by(Case(*ordering_conditions, default=0))
                    print("------experience is high but no country selected------")

            elif experience_filter and experience_filter == "low":
                if country_filter:
                    country_id_int = int(country_filter)
                    country = Countries.objects.get(country_id=country_id_int)
                    # consultant_details = ConsultantDetails.objects.filter(consultant_id__in=queryset, consultant_countries__in=[country]).order_by('-experience')
                    ordering_conditions = [
                        When(consultant_id=user_id, then=pos)
                        for pos, user_id in enumerate(queryset, start=1)
                    ]
                    consultant_details = ConsultantDetails.objects.filter(
                        consultant_id__in=queryset, consultant_countries__in=[country]
                    ).order_by(Case(*ordering_conditions, default=0))
                    print("------experience is low and country is there------")

                else:
                    # consultant_details = ConsultantDetails.objects.filter(consultant_id__in=queryset).order_by('-experience')
                    ordering_conditions = [
                        When(consultant_id=user_id, then=pos)
                        for pos, user_id in enumerate(queryset, start=1)
                    ]
                    consultant_details = ConsultantDetails.objects.filter(
                        consultant_id__in=queryset
                    ).order_by(Case(*ordering_conditions, default=0))
                    print("------experience is low but no country selected------")

            else:
                if country_filter:
                    country_id_int = int(country_filter)
                    country = Countries.objects.get(country_id=country_id_int)
                    # consultant_details = ConsultantDetails.objects.filter(consultant_id__in=queryset, consultant_countries__in=[country])

                    ordering_conditions = [
                        When(consultant_id=user_id, then=pos)
                        for pos, user_id in enumerate(queryset, start=1)
                    ]
                    consultant_details = ConsultantDetails.objects.filter(
                        consultant_id__in=queryset, consultant_countries__in=[country]
                    ).order_by(Case(*ordering_conditions, default=0))

                    consultant_details_ids = list(
                        consultant_details.values_list("consultant_id", flat=True)
                    )
                    user_ordering_conditions = [
                        When(id=user_id, then=pos)
                        for pos, user_id in enumerate(consultant_details_ids, start=1)
                    ]
                    consultant_users = Users.objects.filter(
                        id__in=consultant_details_ids
                    ).order_by(Case(*user_ordering_conditions, default=0))

                    queryset = list(consultant_users.values_list("id", flat=True))

                    print("------no experience but country is there------")
                    print("---------consultant_details-------: ", consultant_details)
                    print("user_ordering_conditions: ", user_ordering_conditions)

                else:
                    # consultant_details = ConsultantDetails.objects.filter(consultant_id__in=queryset)
                    ordering_conditions = [
                        When(consultant_id=user_id, then=pos)
                        for pos, user_id in enumerate(queryset, start=1)
                    ]
                    # consultant_details = ConsultantDetails.objects.filter(consultant_id__in=queryset).order_by(Case(*ordering_conditions, default=0))
                    ordering_conditions = [
                        When(consultant_id=user_id, then=pos)
                        for pos, user_id in enumerate(queryset, start=1)
                    ]
                    consultant_details = ConsultantDetails.objects.filter(
                        consultant_id__in=queryset
                    ).order_by(Case(*ordering_conditions, default=0))
                    print("consultant details: ", consultant_details)
                    print("------no experience and no country selected------")

            # consultants_with_details = [{'consultant': consultant, 'details': ConsultantDetails.objects.filter(consultant_id=consultant)} for consultant in queryset]
            print("queryset id: ", queryset)
            consultants_with_details = [
                {
                    "consultant": Users.objects.get(id=consultant),
                    "details": ConsultantDetails.objects.filter(
                        consultant_id=consultant
                    ),
                }
                for consultant in queryset
            ]
            # Sort based on the rating

            # if rating_filter:
            #     consultants_with_details.sort(key=lambda x: x['consultant'].rating or 0, reverse=(rating_filter == 'high'))
            # Sort based on the rating

            # if rating_filter:
            #     consultants_with_details.sort(key=lambda x: x['consultant'].rating or 0, reverse=(rating_filter == 'high'))

            chunked_consultants = [
                consultants_with_details[i]
                for i in range(0, len(consultants_with_details))
            ]
            chunked_consultants = [
                consultants_with_details[i : i + 1]
                for i in range(0, len(consultants_with_details))
            ]
            paginator = Paginator(
                consultants_with_details, 5
            )  # Show 5 consultants per page
            page = request.GET.get("page")

            try:
                chunked_consultants = paginator.page(page)
            except PageNotAnInteger:
                # If page is not an integer, deliver first page.
                chunked_consultants = paginator.page(1)
            except EmptyPage:
                # If page is out of range (e.g., 9999), deliver last page of results.
                chunked_consultants = paginator.page(paginator.num_pages)

            total_search_results = len(consultants_with_details)
            print("chunked consultants: ", chunked_consultants.object_list)
            context = {
                "chunked_consultants": chunked_consultants,
                "search_input": search_input,
                "rating_filter": rating_filter,
                "country_filter": country_filter,
                "experience_filter": experience_filter,
                "total_search_results": total_search_results,
                "page_name": page_name,
                "page_description": page_description,
                "page_keywords": page_keywords,
            }

    context["countries"] = countries
    return render(request, "consultant_list.html", context)


def consultant_list_autosearch(request):
    print(request.GET)
    search = request.GET.get("term")
    payload = []
    if search:
        objs = Users.objects.filter(
            company_name__icontains=search, active_status__in=[1, 3, 4, 5]
        )
        for obj in objs:
            payload.append(obj.company_name)

    return JsonResponse(payload, safe=False)


def colors(request, consultant_id):
    # Get the consultant
    consultant = get_object_or_404(Users, id=consultant_id, user_role=5)

    # Retrieve colors based on the consultant_id
    consultant_colors = Colors.objects.filter(consultant_id=consultant_id).first()

    # Default colors if not found
    default_colors = {
        "header_color": "#03546C",
        "content_color": "#00000",
        "footer_color": "#0c2136;",
    }

    # Use consultant_colors if available, otherwise use default_colors
    colors_data = {
        "header_color": consultant_colors.header_color
        if consultant_colors
        else default_colors["header_color"],
        "content_color": consultant_colors.content_color
        if consultant_colors
        else default_colors["content_color"],
        "footer_color": consultant_colors.footer_color
        if consultant_colors
        else default_colors["footer_color"],
    }

    return JsonResponse(colors_data)


def singel_consultant_base(request, consultant_id):
    # Retrieve the consultant based on the ID
    consultant = get_object_or_404(Users, id=consultant_id, user_role=5)

    # Retrieve additional details from the ConsultantDetails model
    consultant_details = get_object_or_404(
        ConsultantDetails, consultant_id=consultant_id
    )
    print("consultant_details:", consultant_details)
    # Pass the consultant and details to the template
    return render(
        request,
        "consultant_base.html",
        {"consultant": consultant, "consultant_details": consultant_details},
    )


def singel_consultant_details(request, consultant_id):
    consultant = get_object_or_404(Users, id=consultant_id, user_role=5)
    consultant_details = get_object_or_404(
        ConsultantDetails, consultant_id=consultant_id
    )
    consultant_images = list(
        ConsultantImages.objects.filter(consultant_id=consultant_id)
    )
    fav_consultant_ids = []

    try:
        # Assuming dets_regs_id is the user ID
        student_details = StudentDetails.objects.get(dets_regs_id=request.user.id)

        # Split the comma-separated list of favorite consultant IDs
        if student_details.dets_favconsultantlist:
            fav_consultant_ids = [
                int(id) for id in student_details.dets_favconsultantlist.split(",")
            ]
    except ObjectDoesNotExist:
        # Handle the case where StudentDetails does not exist for the user
        student_details = None

    random_image = None
    if consultant_images:
        random_image = random.choice(consultant_images)

    return render(
        request,
        "single-consultant-details.html",
        {
            "consultant": consultant,
            "consultant_details": consultant_details,
            "random_image": random_image,
            "fav_consultant_ids": fav_consultant_ids,
        },
    )


def singel_consultant_page(request, consultant_id):
    consultant = get_object_or_404(Users, id=consultant_id, user_role=5)
    consultant_details = get_object_or_404(
        ConsultantDetails, consultant_id=consultant_id
    )

    # Retrieve the corresponding Customizes instance for the current consultant
    customize = Customizes.objects.filter(consultant_id=consultant_id).first()

    page_name = "Home"
    page_description = "'This is a top level student visa related information web portal, you can get any types of information from here. also you can take lates of visa agent information from here.'"
    page_keywords = "'education visa consultant agent in dhaka, student visa informatin agent, student visa need, student visa consultant company, need student visa from dhaka,'"

    return render(
        request,
        "singel_consultant_page.html",
        {
            "consultant": consultant,
            "consultant_details": consultant_details,
            "customize": customize,
            "page_name": page_name,
            "page_description": page_description,
            "page_keywords": page_keywords,
        },
    )


def singel_consultant_gallery(request, consultant_id):
    consultant = get_object_or_404(Users, id=consultant_id, user_role=5)
    images = ConsultantImages.objects.filter(consultant_id=consultant_id)
    consultant_details = get_object_or_404(
        ConsultantDetails, consultant_id=consultant_id
    )
    consultant_images = ConsultantImages.objects.filter(consultant_id=consultant_id)
    page_name = "Gallery"
    page_description = "'This is a top level student visa related information web portal, you can get any types of information from here. also you can take lates of visa agent information from here.'"
    page_keywords = "'education visa consultant agent in dhaka, student visa informatin agent, student visa need, student visa consultant company, need student visa from dhaka,'"

    return render(
        request,
        "singel_consultant_gallery.html",
        {
            "consultant": consultant,
            "consultant_details": consultant_details,
            "consultant_images": consultant_images,
            "page_name": page_name,
            "images": images,
            "page_description": page_description,
            "page_keywords": page_keywords,
        },
    )


def single_consultant_requirement(request, consultant_id):
    consultant = get_object_or_404(Users, id=consultant_id, user_role=5)
    consultant_details = get_object_or_404(
        ConsultantDetails, consultant_id=consultant_id
    )
    page_name = "Requirement"
    page_description = "'This is a top level student visa related information web portal, you can get any types of information from here. also you can take lates of visa agent information from here.'"
    page_keywords = "'education visa consultant agent in dhaka, student visa informatin agent, student visa need, student visa consultant company, need student visa from dhaka,'"

    print("Consultant details: ", consultant_details)
    print("Consultant details: ", consultant_details.consultant_requirement)
    # Splitting and slicing the consultant_requirement
    if consultant_details.consultant_requirement:
        requirement_lines = consultant_details.consultant_requirement.split("\n")
        first_line = requirement_lines[0]
        middle_lines = requirement_lines[1:-1]
        last_line = requirement_lines[-1]

    else:
        first_line = ""
        middle_lines = ""
        last_line = ""

    context = {
        "consultant": consultant,
        "consultant_details": consultant_details,
        "first_line": first_line,
        "middle_lines": middle_lines,
        "last_line": last_line,
        "page_name": page_name,
        "page_description": page_description,
        "page_keywords": page_keywords,
    }

    return render(request, "singel_consultant_requirement.html", context)


def singel_consultant_country(request, consultant_id):
    consultant = get_object_or_404(Users, id=consultant_id, user_role=5)
    consultant_details = get_object_or_404(
        ConsultantDetails, consultant_id=consultant_id
    )
    page_name = "Country"
    page_description = "'This is a top level student visa related information web portal, you can get any types of information from here. also you can take lates of visa agent information from here.'"
    page_keywords = "'education visa consultant agent in dhaka, student visa informatin agent, student visa need, student visa consultant company, need student visa from dhaka,'"

    consultant_countries = Countries.objects.filter(
        consultant_details=consultant_details
    )

    # Number of items per page
    items_per_page = 12

    paginator = Paginator(consultant_countries, items_per_page)

    page = request.GET.get("page")

    try:
        consultant_countries = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        consultant_countries = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        consultant_countries = paginator.page(paginator.num_pages)

    return render(
        request,
        "singel_consultant_country.html",
        {
            "consultant_details": consultant_details,
            "consultant": consultant,
            "consultant_countries": consultant_countries,
            "page_name": page_name,
            "page_description": page_description,
            "page_keywords": page_keywords,
        },
    )


def singel_consultant_country_details(request, consultant_id, country_id):
    consultant = get_object_or_404(Users, id=consultant_id, user_role=5)
    consultant_details = get_object_or_404(
        ConsultantDetails, consultant_id=consultant_id
    )
    country = get_object_or_404(Countries, country_id=country_id)
    page_name = "Country Details"
    page_description = "'This is a top level student visa related information web portal, you can get any types of information from here. also you can take lates of visa agent information from here.'"
    page_keywords = "'education visa consultant agent in dhaka, student visa informatin agent, student visa need, student visa consultant company, need student visa from dhaka,'"

    country_howtoapply = mark_safe(country.country_howtoapply)
    return render(
        request,
        "singel_consultant_country_details.html",
        {
            "consultant_details": consultant_details,
            "consultant": consultant,
            "country": country,
            "country_howtoapply": country_howtoapply,
            "page_name": page_name,
            "page_description": page_description,
            "page_keywords": page_keywords,
        },
    )


def singel_consultant_review(request, consultant_id):
    consultant = get_object_or_404(Users, id=consultant_id, user_role=5)
    consultant_details = get_object_or_404(
        ConsultantDetails, consultant_id=consultant_id
    )

    reviews = Review.objects.filter(consultant=consultant_id).order_by("-created_at")[
        :10
    ]

    # Create a list to store review data
    reviews_data = []

    # Fetch related students and users
    for review in reviews:
        student = Students.objects.get(id=review.student)
        student_details = StudentDetails.objects.filter(
            dets_regs_id=review.student
        ).first()

        # Create a dictionary to store review data
        review_data = {
            "id": review.id,
            "student_name": student.full_name,
            "rating": review.rating,
            "image_url": student_details.student_image.url
            if student_details and student_details.student_image
            else None,
            "address": student.address,
            "comment": review.comment,
            "created_at": review.created_at.strftime("%Y-%m-%d %H:%M:%S"),
        }

        reviews_data.append(review_data)

    page_name = "Review"
    page_description = "'This is a top level student visa related information web portal, you can get any types of information from here. also you can take lates of visa agent information from here.'"
    page_keywords = "'education visa consultant agent in dhaka, student visa informatin agent, student visa need, student visa consultant company, need student visa from dhaka,'"
    context = {
        "page_name": page_name,
        "reviews_data": reviews_data,
        "page_description": page_description,
        "page_keywords": page_keywords,
    }

    # if request.user.is_authenticated:
    user = request.user
    context["consultant"] = consultant
    context["consultant_details"] = consultant_details

    student = Students.objects.filter(id=user.id).first()
    if student is not None:
        rating = Review.objects.filter(
            consultant=consultant_id, student=student.id
        ).first()

        if rating is not None:
            student_raw_rating = rating.raw_rating
            student_rating = rating.rating
            context["student_rating"] = student_rating
            context["student_raw_rating"] = student_raw_rating
            print("student rating: ", student_rating)

    if not request.user.is_authenticated:
        request.session["next_page"] = request.path
        request.session["consultant_id"] = consultant.id

        if "last_activity_time" not in request.session:
            request.session["last_activity_time"] = timezone.now().isoformat()
        else:
            # Update the last activity time on each request
            request.session["last_activity_time"] = timezone.now().isoformat()

        # Check if the session has been inactive for 10 minutes
        if "last_activity_time" in request.session:
            last_activity_time = datetime.fromisoformat(
                request.session["last_activity_time"]
            )
            current_time = timezone.now()
            if (
                current_time - last_activity_time
            ).total_seconds() > 300:  # 5 minutes = 300 seconds
                # Destroy the session if inactive for more than 10 minutes
                # request.session.flush()
                del request.session["next_page"]
                del request.session["last_activity_time"]
                request.session.modified = True

        print("request session after 10 seconds: ", request.session["next_page"])

    return render(request, "singel_consultant_review.html", context)


def save_review(request):
    if request.method == "POST":
        raw_rating_str = request.POST.get("raw_rating")
        comment = request.POST.get("comment")
        if request.user.is_authenticated:
            if raw_rating_str or comment:
                raw_rating = int(raw_rating_str)
                consultant_id = request.POST.get("consultant_id")
                consultant = Users.objects.filter(id=consultant_id).first()
                student = Students.objects.filter(id=request.user.id).first()
                print("consultant: ", consultant)
                print("student: ", student)
                captcha_token = request.POST.get("g-recaptcha-response")

                # Perform reCAPTCHA verification
                cap_url = "https://www.google.com/recaptcha/api/siteverify"
                cap_secret = "6LcxvG8pAAAAAIaMvcT9M_ys9A7ytKR1UCIZFvKW"
                cap_data = {"secret": cap_secret, "response": captcha_token}
                cap_server_response = requests.post(url=cap_url, data=cap_data)
                cap_json = json.loads(cap_server_response.text)

                if not captcha_token:
                    return JsonResponse(
                        {"error": "Please complete the reCAPTCHA verification"},
                        status=400,
                    )

                if cap_json.get("success", False):
                    if student and consultant:
                        if raw_rating:
                            rating = round(raw_rating, 1)

                            student_rating = Review.objects.filter(
                                consultant=consultant_id, student=student.id
                            ).first()
                            maximum_review = Review.objects.filter(student=student.id)
                            print(
                                "number of review by the student: ", len(maximum_review)
                            )
                            if student_rating is None:
                                if len(maximum_review) < 5:
                                    print("student rating new: ", student_rating)

                                    review = Review(
                                        consultant=consultant.id,
                                        student=student.id,
                                        raw_rating=raw_rating,
                                        rating=rating,
                                    )

                                    if comment:
                                        review.comment = comment

                                    review.save()

                                    return JsonResponse({"success": True})

                                else:
                                    return JsonResponse(
                                        {
                                            "error": "You can review at most 5 consultants"
                                        }
                                    )

                            elif student_rating is not None:
                                print("student rating has: ", student_rating)
                                student_rating.raw_rating = raw_rating
                                student_rating.rating = rating

                                if comment:
                                    student_rating.comment = comment

                                student_rating.save()

                                return JsonResponse({"success": True})

                        else:
                            return JsonResponse({"error": "Rating is required"})

                    else:
                        return JsonResponse(
                            {
                                "wrong_user_error": "Not permitted to post a review. You need to be a student to post a review."
                            }
                        )

                else:
                    return JsonResponse({"error": "Inavlid Captcha"})

            else:
                return JsonResponse({"error": "At least rating is required"})

        else:
            return JsonResponse(
                {"no_user_error": "You need to login as a student to post a review"}
            )

    else:
        return JsonResponse({"error": "Invalid Request"})


def single_consultant_all_reviews(request, consultant_id):
    consultant = get_object_or_404(Users, id=consultant_id, user_role=5)
    consultant_details = get_object_or_404(
        ConsultantDetails, consultant_id=consultant_id
    )

    reviews = Review.objects.filter(consultant=consultant_id)

    # Create a list to store review data
    all_reviews = []

    # Fetch related students and users
    for review in reviews:
        student = Students.objects.get(id=review.student)
        student_details = StudentDetails.objects.filter(
            dets_regs_id=review.student
        ).first()

        # Create a dictionary to store review data
        review_data = {
            "id": review.id,
            "student_name": student.full_name,
            "rating": review.rating,
            "image_url": student_details.student_image.url
            if student_details and student_details.student_image
            else None,
            "address": student.address,
            "comment": review.comment,
            "created_at": review.created_at.strftime("%Y-%m-%d %H:%M:%S"),
        }

        all_reviews.append(review_data)

    page_name = "Review"

    page_description = "This is a top level student visa related information web portal, you can get any types of information from here. also you can take lates of visa agent information from here."
    page_keywords = "education visa consultant agent in dhaka, student visa informatin agent, student visa need, student visa consultant company, need student visa from dhaka,"

    paginator = Paginator(all_reviews, 10)

    page = request.GET.get("page")

    try:
        reviews_data = paginator.page(page)
    except PageNotAnInteger:
        reviews_data = paginator.page(1)

    except EmptyPage:
        # If page is out of range (e.g., 9999), deliver the last page.
        reviews_data = paginator.page(paginator.num_pages)

    context = {
        "page_name": page_name,
        "page_description": page_description,
        "page_keywords": page_keywords,
        "reviews_data": reviews_data,
        "consultant": consultant,
    }

    return render(request, "single_consultant_all_reviews.html", context)


def singel_consultant_profile(request, consultant_id):
    consultant = get_object_or_404(Users, id=consultant_id, user_role=5)
    page_name = "Profile"

    page_description = "This is a top level student visa related information web portal, you can get any types of information from here. also you can take lates of visa agent information from here."
    page_keywords = "education visa consultant agent in dhaka, student visa informatin agent, student visa need, student visa consultant company, need student visa from dhaka,"

    consultant_details = get_object_or_404(
        ConsultantDetails, consultant_id=consultant_id
    )
    return render(
        request,
        "singel_consultant_profile.html",
        {
            "consultant_details": consultant_details,
            "consultant": consultant,
            "page_name": page_name,
            "page_description": page_description,
            "page_keywords": page_keywords,
        },
    )


def feedback(request, consultant_id):
    consultant = get_object_or_404(Users, id=consultant_id, user_role=5)

    consultant_details = get_object_or_404(
        ConsultantDetails, consultant_id=consultant.id
    )

    countries = consultant_details.consultant_countries.all()

    page_name = "Feedback"

    context = {"consultant": consultant, "countries": countries, "page_name": page_name}

    return render(request, "feedback.html", context)


def save_feedback(request):
    if request.method == "POST":
        # Extract form data
        name = request.POST.get("username")
        email = request.POST.get("email")
        phone = request.POST.get("phone")
        subject = request.POST.get("subject")
        country_ids = request.POST.getlist(
            "country"
        )  # Extract multiple selected countries as a list
        message = request.POST.get("message")
        consultant_id = request.POST.get("consultantId")
        captcha_token = request.POST.get("g-recaptcha-response")

        print("country_ids: ", country_ids)

        # country_list = Countries.objects.filter(country_id__in=country_ids)
        country_ids_str = ", ".join(map(str, country_ids))
        # country_names = [country.country_name for country in countries]
        # print('countries: ', countries)
        print("country names: ", country_ids_str)

        # Perform reCAPTCHA verification
        cap_url = "https://www.google.com/recaptcha/api/siteverify"
        cap_secret = "6LcxvG8pAAAAAIaMvcT9M_ys9A7ytKR1UCIZFvKW"
        cap_data = {"secret": cap_secret, "response": captcha_token}
        cap_server_response = requests.post(url=cap_url, data=cap_data)
        cap_json = json.loads(cap_server_response.text)
        if not captcha_token:
            return JsonResponse(
                {"error": "Please complete the reCAPTCHA verification"}, status=400
            )

        if cap_json.get("success", False):
            # Check if all required form fields are provided
            if name and email and phone and subject and country_ids and message:
                # Validate email format
                if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
                    return JsonResponse({"error": "Invalid email format"}, status=400)

                # Validate phone number format
                if not re.match(r"^\d{11}$", phone):
                    return JsonResponse(
                        {"error": "Invalid phone number format"}, status=400
                    )

                # Create feedback object for each selected country
                # for country_id in countries:
                feedback = HomeFeedback.objects.create(
                    consultant=consultant_id,
                    fdk_fullname=name,
                    fdk_email=email,
                    fdk_phone=phone,
                    fdk_msg=message,
                    country=country_ids_str,
                    subject=subject,
                    created_at=timezone.now(),
                )

                # Add student ID if authenticated
                if request.user.is_authenticated:
                    user = request.user
                    if user.user_type == 2:
                        student_id = request.user.id
                        feedback.student = student_id

                feedback.save()

                return JsonResponse({"success": True})
            else:
                # Missing required fields
                return JsonResponse(
                    {"error": "Please fill up all the required fields"}, status=400
                )
        else:
            # reCAPTCHA verification failed
            return JsonResponse(
                {"error": "reCAPTCHA verification failed. Please try again."},
                status=400,
            )
    else:
        # Invalid request method
        return JsonResponse({"error": "Invalid request"}, status=400)


def singel_consultant_contact(request, consultant_id):
    print(f"Consultant ID: {consultant_id}")
    page_name = "Contact"
    page_description = "This is a top level student visa related information web portal, you can get any types of information from here. also you can take lates of visa agent information from here."
    page_keywords = "education visa consultant agent in dhaka, student visa informatin agent, student visa need, student visa consultant company, need student visa from dhaka,"

    try:
        consultant = get_object_or_404(Users, id=consultant_id, user_role=5)
        consultant_details = get_object_or_404(
            ConsultantDetails, consultant_id=consultant_id
        )
    except Http404:
        # Handle 404 error here, render a custom 404 template
        return render(request, "error.html", status=404)

    return render(
        request,
        "singel_consultant_contact.html",
        {
            "consultant_details": consultant_details,
            "consultant": consultant,
            "page_name": page_name,
            "page_description": page_description,
            "page_keywords": page_keywords,
        },
    )


def consaltant_wise_scholarship(request):
    # Fetch scholarships from the database
    scholarships = ScholarShips.objects.filter(status=1)
    page_name = "Scholarship | Consaltant Wise"
    page_description = "This is a top level student visa related information web portal, you can get any types of information from here. also you can take lates of visa agent information from here."
    page_keywords = "education visa consultant agent in dhaka, student visa informatin agent, student visa need, student visa consultant company, need student visa from dhaka,"
    consultant_wise_scholarships = ConsultantWises.objects.all()

    # Fetch user details for consultants
    consultant_users = Users.objects.filter(
        user_role=5
    )  # Assuming user_role 5 corresponds to consultants

    # Pass scholarships, consultant details, and consultant users to the template context
    context = {
        "scholarships": scholarships,
        "consultant_users": consultant_users,
        "page_name": page_name,
        "page_description": page_description,
        "page_keywords": page_keywords,
        "consultant_wise_scholarships": consultant_wise_scholarships,
    }

    # Render the template with the context
    return render(request, "consaltant_wise.html", context)


@login_required(login_url="login_student")
def consaltant_wise_scholarship_singel_page(request, scholarship_id):
    # Fetch a specific scholarship using the provided scholarship_id
    # Fetch a specific scholarship using the provided scholarship_id
    scholarship = ScholarShips.objects.filter(id=scholarship_id).first()
    consultant_wise_scholarship = None

    if not scholarship:
        # If scholarship with scholarship_id is not found, try to fetch using scow_id
        consultant_wise_scholarship = get_object_or_404(
            ConsultantWises, scow_id=scholarship_id
        )

    # Assuming user_role 5 corresponds to consultants
    consultant_users = Users.objects.filter(user_role=5)
    page_name = "Scholarship | Consultant Wise | Details"
    page_description = "This is a top level student visa related information web portal, you can get any types of information from here. also you can take lates of visa agent information from here."
    page_keywords = "education visa consultant agent in dhaka, student visa informatin agent, student visa need, student visa consultant company, need student visa from dhaka,"

    context = {
        "scholarship": scholarship,
        "consultant_users": consultant_users,
        "consultant_wise_scholarship": consultant_wise_scholarship,
        "page_name": page_name,
        "page_description": page_description,
        "page_keywords": page_keywords,
    }

    # Render the template with the context
    return render(request, "scholarship_singel_page.html", context)


def country_wise_scholarship(request):
    # Get all instances of CountryWises
    country_wise_list = CountryWises.objects.all()
    page_name = "Scholarship | Country Wise "
    page_description = "This is a top level student visa related information web portal, you can get any types of information from here. also you can take lates of visa agent information from here."
    page_keywords = "education visa consultant agent in dhaka, student visa informatin agent, student visa need, student visa consultant company, need student visa from dhaka,"

    # Set the number of items per page
    items_per_page = 9

    # Create a Paginator object
    paginator = Paginator(country_wise_list, items_per_page)

    # Get the current page number from the request's GET parameters
    page = request.GET.get("page")

    try:
        # Get the Page object for the current page
        country_wise = paginator.page(page)
    except PageNotAnInteger:
        # If the page parameter is not an integer, set it to the first page
        country_wise = paginator.page(1)
    except EmptyPage:
        # If the page parameter is out of range, deliver the last page of results
        country_wise = paginator.page(paginator.num_pages)

    return render(
        request,
        "country_wise_scholarship.html",
        {
            "country_wise": country_wise,
            "page_name": page_name,
            "page_description": page_description,
            "page_keywords": page_keywords,
        },
    )


@login_required(login_url="login_student")
def country_wise_scholarship_single(request, scw_id):
    scholarship = get_object_or_404(CountryWises, scw_id=scw_id)
    page_name = "Scholarship | Country Wise|Details"
    page_description = "This is a top level student visa related information web portal, you can get any types of information from here. also you can take lates of visa agent information from here."
    page_keywords = "education visa consultant agent in dhaka, student visa informatin agent, student visa need, student visa consultant company, need student visa from dhaka,"
    return render(
        request,
        "country_wise_scholarship_single.html",
        {
            "scholarship": scholarship,
            "page_name": page_name,
            "page_description": page_description,
            "page_keywords": page_keywords,
        },
    )


def offer_letter(request):
    offer_letters = OfferLetters.objects.all()
    customizes = Customizes.objects.all()  # Fetch Customizes data

    root_users = CustomUser.objects.filter(user_type=0)
    customize_benefit = Customizes.objects.filter(consultant__in=root_users).last()

    page_name = "Offer Letter"
    page_description = "This is a top level student visa related information web portal, you can get any types of information from here. also you can take lates of visa agent information from here."
    page_keywords = "education visa consultant agent in dhaka, student visa informatin agent, student visa need, student visa consultant company, need student visa from dhaka,"

    context = {
        "offer_letters": offer_letters,
        "customizes": customizes,
        "page_name": page_name,
        "customize_benefit": customize_benefit,
        "page_keywords": page_keywords,
    }
    return render(request, "offer_letter.html", context)


def by_country(request):
    if request.method == "GET":
        search_input = request.GET.get("search_area")
        print("search_input: ", search_input)

        if search_input:
            countries_list = Countries.objects.filter(
                country_name__icontains=search_input
            )
        else:
            countries_list = Countries.objects.all()

    paginator = Paginator(countries_list, 12)
    page_name = "Offer Letter | By Country "

    page = request.GET.get("page")
    page_description = "This is a top level student visa related information web portal, you can get any types of information from here. also you can take lates of visa agent information from here."
    page_keywords = "education visa consultant agent in dhaka, student visa informatin agent, student visa need, student visa consultant company, need student visa from dhaka,"

    try:
        countries = paginator.page(page)

    except PageNotAnInteger:
        countries = paginator.page(1)

    except EmptyPage:
        # If page is out of range (e.g., 9999), deliver the last page.
        countries = paginator.page(paginator.num_pages)

    for i in countries.paginator.page_range:
        if (
            i <= 5
            or i > countries.paginator.num_pages - 2
            or (i > countries.number - 2 and i < countries.number + 2)
        ):
            print("page number: ", i)

    print("countries", countries)
    context = {
        "countries": countries,
        "page_name": page_name,
        "page_description": page_description,
        "page_keywords": page_keywords,
    }
    return render(request, "by_country.html", context)


def by_country_autosearch(request):
    print(request.GET)
    search = request.GET.get("term")

    payload = []
    if search:
        objs = Countries.objects.filter(country_name__icontains=search)
        for obj in objs:
            payload.append(obj.country_name)

    return JsonResponse(payload, safe=False)


def country_details(request, country_id):
    page_name = "Offer Letter | By Country | Country Details "

    page_description = "This is a top level student visa related information web portal, you can get any types of information from here. also you can take lates of visa agent information from here."
    page_keywords = "education visa consultant agent in dhaka, student visa informatin agent, student visa need, student visa consultant company, need student visa from dhaka,"
    country = Countries.objects.get(country_id=country_id)

    context = {
        "country": country,
        "page_name": page_name,
        "page_description": page_description,
        "page_keywords": page_keywords,
    }
    return render(request, "country_details.html", context)


# Student Dashboard


@login_required(login_url="login_student")
def student_home(request):
    page_name = "Home"
    page_description = "This is a top level student visa related information web portal, you can get any types of information from here. also you can take lates of visa agent information from here."
    page_keywords = "education visa consultant agent in dhaka, student visa informatin agent, student visa need, student visa consultant company, need student visa from dhaka,"

    user_id = request.user.id

    try:
        student = Students.objects.get(id=user_id)
    except Students.DoesNotExist:
        return redirect("login_student")

    # Printing request.user
    print("Current user:", request.user)

    context = {
        "student": student,
        "page_name": page_name,
        "page_description": page_description,
        "page_keywords": page_keywords,
    }

    return render(request, "studentinfo/home.html", context)


@login_required(login_url="login_student")
def student_search_consultant(request):
    query = request.GET.get("q")
    page_name = "Search Counsultant"
    page_description = "This is a top level student visa related information web portal, you can get any types of information from here. also you can take lates of visa agent information from here."
    page_keywords = "education visa consultant agent in dhaka, student visa informatin agent, student visa need, student visa consultant company, need student visa from dhaka,"

    user = request.user

    # Filter consultants with user_role=5 and active_status not equal to 0 or 2
    consultants = Users.objects.filter(user_role=5, active_status__in=[1, 3, 4, 5])

    if query:
        consultants = consultants.filter(company_name__icontains=query)

    # Pagination
    paginator = Paginator(consultants, 5)  # Show 10 consultants per page
    page = request.GET.get("page")

    try:
        consultants = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        consultants = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        consultants = paginator.page(paginator.num_pages)

    context = {
        "consultants": consultants,
        "query": query,
        "user": user,
        "page_name": page_name,
        "page_description": page_description,
        "page_keywords": page_keywords,
    }

    return render(request, "studentinfo/consultant_search.html", context)


@login_required(login_url="login_student")
def add_to_favorite(request, consultant_id):
    consultant = get_object_or_404(Users, pk=consultant_id)
    page_name = "Add Favorite"

    page_description = "This is a top level student visa related information web portal, you can get any types of information from here. also you can take lates of visa agent information from here."
    page_keywords = "education visa consultant agent in dhaka, student visa informatin agent, student visa need, student visa consultant company, need student visa from dhaka,"

    student_details, created = StudentDetails.objects.get_or_create(
        dets_regs_id=request.user.id
    )

    fav_consultant_list = student_details.dets_favconsultantlist

    if fav_consultant_list:
        fav_consultant_list += f",{consultant_id}"
    else:
        fav_consultant_list = consultant_id

    student_details.dets_favconsultantlist = fav_consultant_list
    student_details.save()

    messages.success(
        request, f"{consultant.full_name} added to favorites successfully."
    )

    return redirect("student_favourite_list")


@login_required(login_url="login_student")
def student_favourite_list(request):
    page_name = "Favorite Consultant List"

    page_description = "This is a top level student visa related information web portal, you can get any types of information from here. also you can take lates of visa agent information from here."
    page_keywords = "education visa consultant agent in dhaka, student visa informatin agent, student visa need, student visa consultant company, need student visa from dhaka,"
    try:
        student_details = StudentDetails.objects.get(dets_regs_id=request.user.id)
    except StudentDetails.DoesNotExist:
        student_details = None

    if student_details:
        fav_consultant_list = student_details.dets_favconsultantlist
        consultant_ids = fav_consultant_list.split(",") if fav_consultant_list else []

        favorite_consultants = Users.objects.filter(pk__in=consultant_ids)

        # Fetch consultant statuses
        consultant_statuses = ConsultantStatus.objects.filter(
            student=student_details, consultant_id__in=consultant_ids
        )

        # Create a dictionary to store statuses
        status_dict = {status.consultant_id: status for status in consultant_statuses}

        # Create a list of dictionaries containing consultant details and status
        consultant_list = [
            {
                "consultant": consultant,
                "status": status_dict.get(consultant.id, None),
                "total_reviews": Review.objects.filter(
                    consultant=consultant.id
                ).count(),  # Count total reviews for the consultant
            }
            for consultant in favorite_consultants
        ]

        context = {
            "consultant_list": consultant_list,
            "page_name": page_name,
            "page_description": page_description,
            "page_keywords": page_keywords,
        }
    else:
        context = {
            "consultant_list": None,
            "page_name": page_name,
            # Set consultant_list to None if student_details is None
        }

    return render(request, "studentinfo/student_favourite_consultant.html", context)


@login_required(login_url="login_student")
def delete_favourite_consultant(request, consultant_id):
    try:
        print("Delete view is called.")

        # Get the current user's student details
        student_details = StudentDetails.objects.get(dets_regs_id=request.user.id)

        # Get the list of favorite consultants
        fav_consultant_list = student_details.dets_favconsultantlist

        # Split the list into consultant IDs
        consultant_ids = fav_consultant_list.split(",") if fav_consultant_list else []

        # Convert the consultant_id to a string for comparison
        consultant_id_str = str(consultant_id)

        # Remove the selected consultant ID from the list
        if consultant_id_str in consultant_ids:
            consultant_ids.remove(consultant_id_str)

        # Join the updated list back into a string
        student_details.dets_favconsultantlist = ",".join(consultant_ids)

        # Save the updated student details
        student_details.save()

        # Prepare a JSON response
        response_data = {
            "status": "success",
            "message": "Consultant removed from favorites.",
        }

    except StudentDetails.DoesNotExist:
        response_data = {"status": "error", "message": "Student details not found."}

    print("Response data:", response_data)
    return JsonResponse(response_data)


@login_required(login_url="login_student")
def student_result_information(request):
    student_id = request.user.id
    existing_results = Results.objects.filter(student_id=student_id).first()
    course_names = CourseName.objects.all()
    masters_degrees = MastersDegree.objects.filter(student_id=student_id).order_by(
        "-passing_year"
    )[:2]
    other_certifications = OtherCertification.objects.filter(student_id=student_id)
    page_name = "Student Result information"

    page_description = "This is a top level student visa related information web portal, you can get any types of information from here. also you can take lates of visa agent information from here."
    page_keywords = "education visa consultant agent in dhaka, student visa informatin agent, student visa need, student visa consultant company, need student visa from dhaka,"
    current_year = datetime.now().year

    passing_years = list(range(1990, current_year + 1))

    with open("static/assets/json/bd_universities.json") as json_file:
        bd_universities = json.load(json_file)

    context = {
        "existing_results": existing_results,
        "page_name": page_name,
        "page_description": page_description,
        "page_keywords": page_keywords,
        "passing_years": passing_years,
        "bd_universities": bd_universities,
        "course_names": course_names,
        "masters_degrees": masters_degrees,
        "other_certifications": other_certifications,
    }

    if existing_results is not None:
        existing_secondary_boards = existing_ssc_board_name(existing_results.secondary)
        if existing_results.higher:
            existing_higher_boards = existing_hsc_board_name(existing_results.higher)
            context["existing_higher_boards"] = existing_higher_boards

        context["existing_secondary_boards"] = existing_secondary_boards

    return render(request, "studentinfo/student_result_information.html", context)


# def save_student_result_information(request):
#     if request.method == 'POST':
#         student_id = request.user.id
#         secondary = request.POST.get('secondary')
#         secondary_board = request.POST.get('secondary_board')
#         secondary_result = request.POST.get('secondary_result')
#         secondary_roll_no = request.POST.get('secondary_roll_no')
#         secondary_reg_no = request.POST.get('secondary_reg_no')
#         secondary_certificate_no = request.POST.get('secondary_certificate_no')
#         secondary_passing_year = request.POST.get('secondary_passing_year')

#         higher = request.POST.get('higher')
#         higher_board = request.POST.get('higher_board')
#         higher_result = request.POST.get('higher_result')
#         higher_roll_no = request.POST.get('higher_roll_no')
#         higher_reg_no = request.POST.get('higher_reg_no')
#         higher_certificate_no = request.POST.get('higher_certificate_no')
#         higher_passing_year = request.POST.get('higher_passing_year')

#         undergraduation = request.POST.get('undergraduation', '')
#         undergraduation_result = request.POST.get('undergraduation_result', None)
#         if undergraduation_result == 'None':
#             undergraduation_result = None

#         undergraduation_passing_year = request.POST.get('undergraduation_passing_year', None)
#         if undergraduation_passing_year == 'None' or undergraduation_passing_year == 'undefined':
#             undergraduation_passing_year= None

#         university_name = request.POST.get('bd_universities', '')
#         undergraduation_board = request.POST.get('undergraduation_board', '')

#         phd_result = request.POST.get('phd_result', 0)

#         if phd_result == 'None':
#             phd_result = None

#         phd_passing_year = request.POST.get('phd_passing_year', None)

#         if phd_passing_year == 'None':
#             phd_passing_year = None

#         phd_university = request.POST.get('phd_bd_universities', '')
#         phd_certificate_copy = request.POST.get('phd_certificate_copy', '')
#         phd_board = request.POST.get('phd_board', '')


#         secondary_certificate_copy = request.FILES.get('secondary_certificate_copy', '')
#         higher_certificate_copy = request.FILES.get('higher_certificate_copy', '')
#         undergraduation_certificate_copy = request.FILES.get('undergraduation_certificate_copy', '')

#         # group the values of masters result data
#         formatted_data = []

#         current_group = {}
#         for key, value in request.POST.items():
#             print(f"{key}: ------------------------{value}")
#             if key.startswith('masters_'):
#                 key_parts = key.split('_')
#                 key_suffix = key_parts[-1]
#                 if key_suffix.isdigit():
#                     group_number = int(key_suffix)
#                     attribute_name = '_'.join(key_parts[:-1])  # Extracting the attribute name

#                     if group_number not in current_group:
#                         current_group[group_number] = {}
#                     current_group[group_number][attribute_name] = value


#         # Append each group dictionary to formatted_data
#         formatted_data = list(current_group.values())

#         print('formatted_data:', formatted_data)


#         # group the values of couse data
#         formatted_course_data = []
#         current_course_group = {}
#         for key, value in request.POST.items():
#             print(f"{key}: ------------------------{value}")
#             if key.startswith('course_'):
#                 key_parts = key.split('_')
#                 key_suffix = key_parts[-1]
#                 if key_suffix.isdigit():
#                     group_number = int(key_suffix)
#                     attribute_name = '_'.join(key_parts[:-1])  # Extracting the attribute name

#                     if group_number not in current_course_group:
#                         current_course_group[group_number] = {}
#                     current_course_group[group_number][attribute_name] = value


#         # Append each group dictionary to formatted_course_data
#         formatted_course_data = list(current_course_group.values())

#         print('formatted_course_data:', formatted_course_data)

#         existing_result = Results.objects.filter(student_id=student_id).first()

#         if secondary and secondary_board and secondary_result and secondary_roll_no and secondary_reg_no and secondary_certificate_no and secondary_passing_year  and higher and higher_board and higher_result and higher_roll_no and higher_reg_no and higher_certificate_no and higher_passing_year:
#             # Update or create results
#             if not undergraduation:
#                 undergraduation = 1

#             image_size = 1024 * 1024
#             if secondary_certificate_copy and secondary_certificate_copy.size > image_size:
#                 return JsonResponse({'error': 'Image size of Secondary Education Certificate exeeds 1MB'})

#             if higher_certificate_copy and higher_certificate_copy.size > image_size:
#                 return JsonResponse({'error': 'Image size of Higher Education Certificate exeeds 1MB'})

#             if undergraduation_certificate_copy and undergraduation_certificate_copy.size > image_size:
#                 return JsonResponse({'error': 'Image size of Undergraduation Education Certificate exeeds 1MB'})

#             if existing_result is not None:
#                 if not existing_result.secondary_certificate_copy or not existing_result.higher_certificate_copy:
#                     if not secondary_certificate_copy or not higher_certificate_copy or secondary_certificate_copy is None or higher_certificate_copy is None:
#                         return JsonResponse({'error': 'Please provide both Secondary and Higher Equivalent Certificate images'})

#             results, results_created_at = Results.objects.update_or_create(
#                 student_id=student_id,
#                 defaults={
#                     'secondary': secondary,
#                     'secondary_board': secondary_board,
#                     'secondary_result': secondary_result,
#                     'secondary_roll_no': secondary_roll_no,
#                     'secondary_reg_no': secondary_reg_no,
#                     'secondary_certificate_no': secondary_certificate_no,
#                     'secondary_passing_year': secondary_passing_year,
#                     'higher': higher,
#                     'higher_board': higher_board,
#                     'higher_result': higher_result,
#                     'higher_roll_no': higher_roll_no,
#                     'higher_reg_no': higher_reg_no,
#                     'higher_certificate_no': higher_certificate_no,
#                     'higher_passing_year': higher_passing_year,

#                     'undergraduation': undergraduation,
#                     'university_name': university_name,
#                     'undergraduation_board': undergraduation_board,
#                     'updated_at': timezone.now()
#                 }
#             )

#             if secondary_certificate_copy:
#                 if results.secondary_certificate_copy:
#                     default_storage.delete(results.secondary_certificate_copy.path)

#                 results.secondary_certificate_copy = secondary_certificate_copy
#                 results.secondary_certificate_copy.name = certificate_file_path(results, secondary_certificate_copy.name, 'secondary')

#             if higher_certificate_copy:
#                 if results.higher_certificate_copy:
#                     default_storage.delete(results.higher_certificate_copy.path)

#                 results.higher_certificate_copy = higher_certificate_copy
#                 results.higher_certificate_copy.name = certificate_file_path(results, higher_certificate_copy.name, 'higher')

#             if undergraduation_result != '':
#                 results.undergraduation_result = undergraduation_result

#             if undergraduation_passing_year != '':
#                 results.undergraduation_passing_year = undergraduation_passing_year

#             if undergraduation_certificate_copy != '':
#                 if results.undergraduation_certificate_copy:
#                     default_storage.delete(results.undergraduation_certificate_copy.path)

#                 results.undergraduation_certificate_copy = undergraduation_certificate_copy
#                 results.undergraduation_certificate_copy.name = certificate_file_path(results, undergraduation_certificate_copy.name, 'ungraduation')

#             if phd_result:
#                 results.phd_result = phd_result

#             if phd_passing_year:
#                 results.phd_passing_year = phd_passing_year

#             if phd_university:
#                 results.phd_university = phd_university

#             if phd_certificate_copy:
#                 if results.phd_certificate_copy:
#                     default_storage.delete(results.phd_certificate_copy.path)

#                 results.phd_certificate_copy = phd_certificate_copy
#                 results.phd_certificate_copy.name = certificate_file_path(results, phd_certificate_copy.name, 'Phd')

#             if phd_board:
#                 results.phd_board = phd_board

#             results.save()

#             # Saving Masters data
#             print('formatted_data length: ', len(formatted_data))
#             masters_degrees = MastersDegree.objects.filter(student_id=student_id)
#             masters_degrees.delete()
#             # Loop through the masters data and save each of them
#             for group_number, data in enumerate(formatted_data):
#                 # Extract data from the dictionary with default values or None if undefined, null, or empty
#                 result = float(data.get('masters_result', 0.0) or 0.0)
#                 passing_year = int(data.get('masters_passing_year', 0) or 0)
#                 department = data.get('masters_department', '')  # Default to empty string if undefined
#                 university = data.get('masters_bd_universities') if data.get('masters_bd_universities') != 'null' else None

#                 certificate_copy_str = f"masters_certificate_copy_{group_number}"
#                 certificate_copy = request.FILES.get(certificate_copy_str, '')

#                 if certificate_copy and certificate_copy.size > image_size:
#                     return JsonResponse({'error': 'Image size of Masters Education Certificate exeeds 1MB'})

#                 print('university: ', university)
#                 print('result: ', result)
#                 print('department: ', department)
#                 print('passing_year: ', passing_year)

#                 if (result != 0.0) and (university is not None or university == 'null'):
#                     print('has masters data')
#                     masters_degree = MastersDegree(
#                         student_id=student_id,
#                         result=result,
#                         passing_year=passing_year,
#                         department=department,
#                         university=university,
#                     )

#                     if certificate_copy:
#                         masters_degree.certificate_copy = certificate_copy
#                     # Save the instance to the database
#                     masters_degree.save()

#                 else:
#                     print('empty masters data')

#                 # else:
#                 #     return JsonResponse()


#             # Saving Course data
#             course_names = CourseName.objects.all()
#             course_names_list = [course_name.name for course_name in course_names]
#             print('course_names_list: ', course_names_list)

#             for group_number, data in enumerate(formatted_course_data):
#                 # Extract data from the dictionary with default values or None if undefined, null, or empty
#                 result = data.get('course_result', '')
#                 passing_year = int(data.get('course_passing_year', 0) or 0)
#                 institute = data.get('course_institution_name', '')  # Default to empty string if undefined

#                 course_name_id = data.get('course_name', '')
#                 print('course_name_id: -----------------------------------------------------', course_name_id)

#                 if course_name_id and institute and result and passing_year != 'undefined' and course_name_id != 'undefined':
#                     course_name = CourseName.objects.get(pk=course_name_id) if course_name_id else None
#                     other_certification = OtherCertification.objects.filter(student_id=student_id, course_name=course_name).first()

#                     certificate_copy_str = f"course_certificate_copy_{group_number}"
#                     certificate_copy = request.FILES.get(certificate_copy_str, '')

#                     if certificate_copy and certificate_copy.size > image_size:
#                         return JsonResponse({'error': 'Image size of Other Courses Certificate exeeds 1MB'})

#                     if other_certification is not None:
#                         if result:
#                             other_certification.result = result

#                         if course_name:
#                             other_certification.course_name = course_name

#                         if institute:
#                             other_certification.institute = institute

#                         if institute:
#                             other_certification.passing_year = passing_year

#                         if certificate_copy and certificate_copy != 'undefined':
#                             other_certification.certificate_copy = certificate_copy

#                     else:
#                         other_certification = OtherCertification(
#                         student_id=student_id,
#                         result=result,
#                         course_name=course_name,
#                         institute=institute,
#                         passing_year=passing_year,
#                     )

#                     if certificate_copy:
#                         other_certification.certificate_copy = certificate_copy

#                     print('other_certifications for the student: ', other_certification)

#                     other_certification.save()

#                 elif(institute or passing_year or result) and (course_name_id == '' or course_name_id == 'undefined' or not course_name_id):
#                     return JsonResponse({'error': f"One or More Academic Certification could not be saved. Please fill up all the details in 'Other Courses' section"})


#             return JsonResponse({'success': True})

#         else:
#             return JsonResponse({'error': 'Please fill up the details in Secondary and Higher section'})

#     return JsonResponse({'error': 'Invalid request method'})


def save_secondary_result_information(request):
    if request.method == "POST":
        student_id = request.user.id
        secondary = request.POST.get("secondary")
        secondary_board = request.POST.get("secondary_board")
        secondary_result = request.POST.get("secondary_result")
        secondary_roll_no = request.POST.get("secondary_roll_no")
        secondary_reg_no = request.POST.get("secondary_reg_no")
        secondary_certificate_no = request.POST.get("secondary_certificate_no")
        secondary_passing_year = request.POST.get("secondary_passing_year")

        secondary_certificate_copy = request.FILES.get("secondary_certificate_copy", "")

        existing_result = Results.objects.filter(student_id=student_id).first()
        student = Students.objects.filter(id=student_id).first()
        print("student status: ", student.status)

        if existing_result and student.status == 2:
            return JsonResponse(
                {
                    "error": f"Your Secondary result has already been verified. You can't change your secondary result."
                }
            )

        else:
            print("entered to save secondary result")
            if (
                secondary
                and secondary_board
                and secondary_result
                and secondary_roll_no
                and secondary_reg_no
                and secondary_certificate_no
                and secondary_passing_year
            ):
                image_size = 1024 * 1024
                if (
                    secondary_certificate_copy
                    and secondary_certificate_copy.size > image_size
                ):
                    return JsonResponse(
                        {
                            "error": "Image size of Secondary Education Certificate exeeds 1MB"
                        }
                    )

                if existing_result is not None:
                    if not existing_result.secondary_certificate_copy:
                        if (
                            not secondary_certificate_copy
                            or secondary_certificate_copy is None
                        ):
                            return JsonResponse(
                                {
                                    "error": "Please provide Secondary Equivalent Certificate images"
                                }
                            )

                results, results_created_at = Results.objects.update_or_create(
                    student_id=student_id,
                    defaults={
                        "secondary": secondary,
                        "secondary_board": secondary_board,
                        "secondary_result": secondary_result,
                        "secondary_roll_no": secondary_roll_no,
                        "secondary_reg_no": secondary_reg_no,
                        "secondary_certificate_no": secondary_certificate_no,
                        "secondary_verification_status": "pending",
                        "secondary_passing_year": secondary_passing_year,
                        "updated_at": timezone.now(),
                    },
                )

                if secondary_certificate_copy:
                    if results.secondary_certificate_copy:
                        default_storage.delete(results.secondary_certificate_copy.path)

                    results.secondary_certificate_copy = secondary_certificate_copy
                    results.secondary_certificate_copy.name = certificate_file_path(
                        results, secondary_certificate_copy.name, "secondary"
                    )

                results.save()

                return JsonResponse({"success": True})
            else:
                return JsonResponse(
                    {"error": "Please fill up the details in Secondary section"}
                )

    return JsonResponse({"error": "Invalid request method"})


def save_higher_result_information(request):
    if request.method == "POST":
        student_id = request.user.id
        higher = request.POST.get("higher", "")
        higher_board = request.POST.get("higher_board", "")
        higher_result = request.POST.get("higher_result", "")
        higher_roll_no = request.POST.get("higher_roll_no", "")
        higher_reg_no = request.POST.get("higher_reg_no", "")
        higher_certificate_no = request.POST.get("higher_certificate_no", "")
        higher_passing_year = request.POST.get("higher_passing_year", "")

        diploma = request.POST.get("diploma", "")
        diploma_board = request.POST.get("diploma_board", "")
        diploma_result = request.POST.get("diploma_result", "")
        diploma_roll_no = request.POST.get("diploma_roll_no", "")
        diploma_reg_no = request.POST.get("diploma_reg_no", "")
        diploma_certificate_no = request.POST.get("diploma_certificate_no", "")
        diploma_passing_year = request.POST.get("diploma_passing_year", "")

        higher_certificate_copy = request.FILES.get("higher_certificate_copy", "")
        diploma_certificate_copy = request.FILES.get("diploma_certificate_copy", "")

        existing_result = Results.objects.filter(student_id=student_id).first()
        student = Students.objects.filter(id=student_id).first()

        if existing_result and student.status == 2:
            return JsonResponse(
                {
                    "error": f"Your Higher Secondary result has already been verified. You can't change your higher secondary result."
                }
            )

        else:
            if (
                higher
                and higher_board
                and higher_result
                and higher_roll_no
                and higher_reg_no
                and higher_certificate_no
                and higher_passing_year
            ):
                image_size = 1024 * 1024
                if (
                    higher_certificate_copy
                    and higher_certificate_copy.size > image_size
                ):
                    return JsonResponse(
                        {
                            "error": "Image size of Secondary Education Certificate exeeds 1MB"
                        }
                    )

                if existing_result is not None:
                    if not existing_result.higher_certificate_copy:
                        if (
                            not higher_certificate_copy
                            or higher_certificate_copy is None
                        ):
                            return JsonResponse(
                                {
                                    "error": "Please provide Higher Equivalent Certificate images"
                                }
                            )

                results, results_created_at = Results.objects.update_or_create(
                    student_id=student_id,
                    defaults={
                        "higher": higher,
                        "higher_board": higher_board,
                        "higher_result": higher_result,
                        "higher_roll_no": higher_roll_no,
                        "higher_reg_no": higher_reg_no,
                        "higher_certificate_no": higher_certificate_no,
                        "higher_verification_status": "pending",
                        "higher_passing_year": higher_passing_year,
                        "updated_at": timezone.now(),
                    },
                )

                if higher_certificate_copy:
                    if results.higher_certificate_copy:
                        default_storage.delete(results.higher_certificate_copy.path)

                    results.higher_certificate_copy = higher_certificate_copy
                    results.higher_certificate_copy.name = certificate_file_path(
                        results, higher_certificate_copy.name, "higher"
                    )

                results.save()

                # Saving Diploma results
                if (
                    diploma_result
                    or diploma_roll_no
                    or diploma_reg_no
                    or diploma_certificate_no
                ):
                    print("got diploma result")
                    if (
                        diploma_board
                        and diploma_result
                        and diploma_roll_no
                        and diploma_reg_no
                        and diploma_certificate_no
                        and diploma_passing_year
                    ):
                        image_size = 1024 * 1024
                        if (
                            diploma_certificate_copy
                            and diploma_certificate_copy.size > image_size
                        ):
                            return JsonResponse(
                                {
                                    "error": "Image size of Diploma Education Certificate exeeds 1MB"
                                }
                            )

                        if existing_result is not None:
                            if not existing_result.secondary_certificate_copy:
                                if (
                                    not higher_certificate_copy
                                    or higher_certificate_copy is None
                                ):
                                    return JsonResponse(
                                        {
                                            "error": "Please provide both Diploma Certificate images"
                                        }
                                    )

                        results, results_created_at = Results.objects.update_or_create(
                            student_id=student_id,
                            defaults={
                                "diploma": diploma,
                                "diploma_board": diploma_board,
                                "diploma_result": diploma_result,
                                "diploma_roll_no": diploma_roll_no,
                                "diploma_reg_no": diploma_reg_no,
                                "diploma_certificate_no": diploma_certificate_no,
                                "diploma_verification_status": "pending",
                                "diploma_passing_year": diploma_passing_year,
                                "updated_at": timezone.now(),
                            },
                        )

                        if diploma_certificate_copy:
                            results.diploma_certificate_copy = diploma_certificate_copy

                        results.save()

                    else:
                        return JsonResponse(
                            {
                                "error": "Please fill up the details in Diploma Education section"
                            }
                        )

                results.save()

                return JsonResponse({"success": True})

            else:
                return JsonResponse(
                    {"error": "Please fill up the details in Higher Education section"}
                )

    return JsonResponse({"error": "Invalid request method"})


def save_undergraduation_result_information(request):
    if request.method == "POST":
        student_id = request.user.id
        undergraduation = request.POST.get("undergraduation", "")
        undergraduation_result = request.POST.get("undergraduation_result", None)
        if undergraduation_result == "None":
            undergraduation_result = None

        undergraduation_passing_year = request.POST.get(
            "undergraduation_passing_year", None
        )
        if (
            undergraduation_passing_year == "None"
            or undergraduation_passing_year == "undefined"
        ):
            undergraduation_passing_year = None

        university_name = request.POST.get("bd_universities", "")
        undergraduation_board = request.POST.get("undergraduation_board", "")
        undergraduation_certificate_copy = request.FILES.get(
            "undergraduation_certificate_copy", ""
        )

        existing_result = Results.objects.filter(student_id=student_id).first()
        student = Students.objects.filter(id=student_id).first()

        # image_size = 1024 * 1024
        # if undergraduation_certificate_copy and undergraduation_certificate_copy.size > image_size:
        #         return JsonResponse({'error': 'Image size of Higher Education Certificate exeeds 1MB'})

        if existing_result and student.status == 2:
            return JsonResponse(
                {
                    "error": f"Your Undergraduation result has already been verified. You can't change your undergraduation result."
                }
            )

        else:
            if undergraduation_result and university_name:
                # if existing_result is not None:
                #     if not existing_result.undergraduation_certificate_copy:
                #         if not undergraduation_certificate_copy or undergraduation_certificate_copy is None:
                #             return JsonResponse({'error': 'Please provide Higher Equivalent Certificate images'})

                if not undergraduation:
                    undergraduation = 12

                results, results_created_at = Results.objects.update_or_create(
                    student_id=student_id,
                    defaults={
                        "undergraduation": undergraduation,
                        "university_name": university_name,
                        "undergraduation_board": undergraduation_board,
                        "undergraduation_verification_status": "pending",
                        "updated_at": timezone.now(),
                    },
                )

                if undergraduation_result != "":
                    results.undergraduation_result = undergraduation_result

                if undergraduation_passing_year != "":
                    results.undergraduation_passing_year = undergraduation_passing_year

                if undergraduation_certificate_copy != "":
                    if results.undergraduation_certificate_copy:
                        default_storage.delete(
                            results.undergraduation_certificate_copy.path
                        )

                    results.undergraduation_certificate_copy = (
                        undergraduation_certificate_copy
                    )
                    results.undergraduation_certificate_copy.name = (
                        certificate_file_path(
                            results,
                            undergraduation_certificate_copy.name,
                            "ungraduation",
                        )
                    )

                results.save()

                return JsonResponse({"success": True})

            else:
                return JsonResponse(
                    {"error": "University name and Current CGPA is required"}
                )

    return JsonResponse({"error": "Invalid request method"})


def save_masters_result_information(request):
    if request.method == "POST":
        student_id = request.user.id
        student = Students.objects.filter(id=student_id).first()

        # group the values of masters result data
        formatted_data = []
        current_group = {}

        if student.status != 2:
            for key, value in request.POST.items():
                print(f"{key}: ------------------------{value}")
                if key.startswith("masters_"):
                    key_parts = key.split("_")
                    key_suffix = key_parts[-1]
                    if key_suffix.isdigit():
                        group_number = int(key_suffix)
                        attribute_name = "_".join(
                            key_parts[:-1]
                        )  # Extracting the attribute name

                        if group_number not in current_group:
                            current_group[group_number] = {}
                        current_group[group_number][attribute_name] = value

            # Append each group dictionary to formatted_data
            formatted_data = list(current_group.values())

            masters_degrees = MastersDegree.objects.filter(student_id=student_id)
            masters_degrees.delete()

            image_size = 1024 * 1024
            # Loop through the masters data and save each of them
            for group_number, data in enumerate(formatted_data):
                # Extract data from the dictionary with default values or None if undefined, null, or empty
                result = float(data.get("masters_result", 0.0) or 0.0)
                passing_year = int(data.get("masters_passing_year", 0) or 0)
                department = data.get(
                    "masters_department", ""
                )  # Default to empty string if undefined
                university = (
                    data.get("masters_bd_universities")
                    if data.get("masters_bd_universities") != "null"
                    else None
                )

                certificate_copy_str = f"masters_certificate_copy_{group_number}"
                certificate_copy = request.FILES.get(certificate_copy_str, "")
                masters_degree_check = MastersDegree.objects.filter(
                    student_id=student_id
                ).first()

                # if certificate_copy and certificate_copy.size > image_size:
                #     return JsonResponse({'error': 'Image size of Masters Education Certificate exeeds 1MB'})

                # if masters_degree_check and masters_degree_check.verification_status != 'verified':
                if (result != 0.0) and (university is not None or university != "null"):
                    print("has masters data")
                    masters_degree = MastersDegree(
                        student_id=student_id,
                        result=result,
                        university=university,
                        verification_status="pending",
                        updated_at=timezone.now(),
                    )

                    if passing_year != "":
                        masters_degree.passing_year = passing_year

                    if department != "":
                        masters_degree.department = department

                    if certificate_copy:
                        masters_degree.certificate_copy = certificate_copy

                    if certificate_copy != "":
                        if masters_degree.certificate_copy:
                            default_storage.delete(masters_degree.certificate_copy.path)

                        masters_degree.certificate_copy = certificate_copy
                        masters_degree.certificate_copy.name = certificate_file_path(
                            masters_degree, certificate_copy.name, "ungraduation"
                        )

                    masters_degree.save()

                else:
                    return JsonResponse(
                        {"error": "University name and Current CGPA is required"}
                    )

            return JsonResponse(
                {
                    "success": True,
                    "success_message": "Only the unverified Masters Degrees Have been saved.",
                }
            )

        else:
            return JsonResponse(
                {
                    "error": f"Your Masters result has already been verified. You can't change your masters result."
                }
            )

    return JsonResponse({"error": "Invalid request method"})


def save_phd_result_information(request):
    if request.method == "POST":
        student_id = request.user.id

        phd_result = request.POST.get("phd_result", 0)

        if phd_result == "None":
            phd_result = None

        phd_passing_year = request.POST.get("phd_passing_year", None)

        if phd_passing_year == "None":
            phd_passing_year = None

        phd_university = request.POST.get("phd_bd_universities", "")
        phd_certificate_copy = request.FILES.get("phd_certificate_copy", "")
        phd_board = request.POST.get("phd_board", "")

        existing_result = Results.objects.filter(student_id=student_id).first()
        student = Students.objects.filter(id=student_id).first()
        # image_size = 1024 * 1024
        # if phd_certificate_copy and phd_certificate_copy.size > image_size:
        #         return JsonResponse({'error': 'Image size of Higher Education Certificate exeeds 1MB'})
        if existing_result and student.status == 2:
            return JsonResponse(
                {
                    "error": f"Your PHD result has verified. You can't change your PHD result."
                }
            )

        else:
            if phd_result and phd_university:
                results, results_created_at = Results.objects.update_or_create(
                    student_id=student_id,
                    defaults={
                        "phd": 1,
                        "phd_result": phd_result,
                        "phd_university": phd_university,
                        "phd_verification_status": "pending",
                        "updated_at": timezone.now(),
                    },
                )

                if phd_passing_year != "":
                    results.phd_passing_year = phd_passing_year

                if phd_certificate_copy != "":
                    if results.phd_certificate_copy:
                        default_storage.delete(results.phd_certificate_copy.path)

                    results.phd_certificate_copy = phd_certificate_copy
                    results.phd_certificate_copy.name = certificate_file_path(
                        results, phd_certificate_copy.name, "phd"
                    )

                results.save()

                return JsonResponse({"success": True})

            else:
                return JsonResponse(
                    {"error": "University name and Current CGPA is required"}
                )

    return JsonResponse({"error": "Invalid request method"})


def save_other_certification_result_information(request):
    if request.method == "POST":
        student_id = request.user.id
        student = Students.objects.filter(id=student_id).first()

        # group the values of couse data
        formatted_course_data = []
        current_course_group = {}

        if student.status != 2:
            for key, value in request.POST.items():
                if key.startswith("course_"):
                    key_parts = key.split("_")
                    key_suffix = key_parts[-1]
                    if key_suffix.isdigit():
                        group_number = int(key_suffix)
                        attribute_name = "_".join(
                            key_parts[:-1]
                        )  # Extracting the attribute name

                        if group_number not in current_course_group:
                            current_course_group[group_number] = {}
                        current_course_group[group_number][attribute_name] = value

            # Append each group dictionary to formatted_course_data
            formatted_course_data = list(current_course_group.values())

            # Saving Course data
            course_names = CourseName.objects.all()
            course_names_list = [course_name.name for course_name in course_names]

            image_size = 1024 * 1024

            for group_number, data in enumerate(formatted_course_data):
                # Extract data from the dictionary with default values or None if undefined, null, or empty
                result = data.get("course_result", "")
                passing_year = int(data.get("course_passing_year", 0) or 0)
                institute = data.get(
                    "course_institution_name", ""
                )  # Default to empty string if undefined

                course_name_id = data.get("course_name", "")

                certificate_copy_str = f"course_certificate_copy_{group_number}"
                certificate_copy = request.FILES.get(certificate_copy_str, "")

                other_courses_check = OtherCertification.objects.filter(
                    student_id=student_id
                ).first()

                # if other_courses_check and other_courses_check.verification_status != 'verified':
                if (
                    course_name_id
                    and institute
                    and result
                    and passing_year != "undefined"
                    and course_name_id != "undefined"
                ):
                    course_name = (
                        CourseName.objects.get(pk=course_name_id)
                        if course_name_id
                        else None
                    )
                    other_certification = OtherCertification.objects.filter(
                        student_id=student_id, course_name=course_name
                    ).first()

                    # certificate_copy_str = f"course_certificate_copy_{group_number}"
                    # certificate_copy = request.FILES.get(certificate_copy_str, '')

                    # if certificate_copy and certificate_copy.size > image_size:
                    #     return JsonResponse({'error': 'Image size of Other Courses Certificate exeeds 1MB'})

                    if other_certification is not None:
                        if not other_certification.certificate_copy:
                            if not certificate_copy or certificate_copy is None:
                                return JsonResponse(
                                    {
                                        "error": "Please provide Academic Certificate images"
                                    }
                                )

                        if result:
                            other_certification.result = result

                        if course_name:
                            other_certification.course_name = course_name

                        if institute:
                            other_certification.institute = institute

                        if passing_year:
                            other_certification.passing_year = passing_year

                        # if certificate_copy and certificate_copy != 'undefined':
                        #     other_certification.certificate_copy = certificate_copy

                        # if certificate_copy:
                        #     if certificate_copy.size > image_size:
                        #         # Open the file and truncate it to 1MB
                        #         with certificate_copy.file as f:
                        #             f.seek(0, 2)  # Move to the end of the file
                        #             file_size = f.tell()
                        #             if file_size > image_size:
                        #                 f.seek(file_size - image_size)  # Move to the position where truncation starts
                        #                 truncated_content = f.read()  # Read content to truncate
                        #                 certificate_copy.file.seek(0)  # Move file pointer to the beginning
                        #                 certificate_copy.file.truncate(0)  # Truncate the file
                        #                 certificate_copy.file.write(truncated_content)  # Write truncated content

                        #                 # new_certificate_copy = certificate_copy
                        #                 certificate_copy.size = certificate_copy.file.tell()
                        #                 print('new_certificate_copy size: ', certificate_copy.size)

                        #                 if other_certification.certificate_copy:
                        #                     # certificate_copy.size = certificate_copy.file.tell()
                        #                     default_storage.delete(other_certification.certificate_copy.path)

                        #                 other_certification.certificate_copy = certificate_copy
                        #                 other_certification.certificate_copy.name = certificate_file_path(other_certification, certificate_copy.name, 'other_certification')

                        if certificate_copy != "":
                            if other_certification.certificate_copy:
                                default_storage.delete(
                                    other_certification.certificate_copy.path
                                )

                            other_certification.certificate_copy = certificate_copy
                            other_certification.certificate_copy.name = (
                                certificate_file_path(
                                    other_certification,
                                    certificate_copy.name,
                                    "other_certification",
                                )
                            )

                    else:
                        other_certification = OtherCertification(
                            student_id=student_id,
                            result=result,
                            course_name=course_name,
                            institute=institute,
                            passing_year=passing_year,
                            verification_status="pending",
                        )

                        if certificate_copy != "":
                            if other_certification.certificate_copy:
                                default_storage.delete(
                                    other_certification.certificate_copy.path
                                )

                            other_certification.certificate_copy = certificate_copy
                            other_certification.certificate_copy.name = (
                                certificate_file_path(
                                    other_certification,
                                    certificate_copy.name,
                                    "other_certification",
                                )
                            )

                    # if certificate_copy:
                    #     other_certification.certificate_copy = certificate_copy

                    print("other_certifications for the student: ", other_certification)

                    other_certification.save()

                elif (institute or passing_year or result) and (
                    course_name_id == ""
                    or course_name_id == "undefined"
                    or not course_name_id
                ):
                    return JsonResponse(
                        {
                            "error": f"One or More Academic Certification could not be saved. Please fill up all the details in 'Other Courses' section"
                        }
                    )

            return JsonResponse(
                {
                    "success": True,
                    "success_message": "Only the unverified Masters Degrees Have been saved.",
                }
            )

        else:
            return JsonResponse(
                {
                    "error": f"Your Extra Courses result has already been verified. You can't change your this result."
                }
            )

    return JsonResponse({"error": "Invalid request method"})


def existing_ssc_board_name(examtype_value):
    if examtype_value == 1:
        ssc_board = {
            "ssc_board": [
                {
                    "1": "Barisal",
                    "2": "Chittagong",
                    "3": "Comilla",
                    "4": "Dhaka",
                    "5": "Dinajpur",
                    "6": "Jessore",
                    "7": "Mymensingh",
                    "8": "Rajshahi",
                    "9": "Sylhet",
                }
            ]
        }

    elif examtype_value == 2:
        ssc_board = {"ssc_board": [{"10": "Edexcel", "11": "Cambridge"}]}

    elif examtype_value == 3:
        ssc_board = {
            "ssc_board": [
                {
                    "1": "Barisal",
                    "2": "Chittagong",
                    "3": "Comilla",
                    "4": "Dhaka",
                    "5": "Dinajpur",
                    "6": "Jessore",
                    "7": "Mymensingh",
                    "8": "Rajshahi",
                    "9": "Sylhet",
                }
            ]
        }

    elif examtype_value == 4:
        ssc_board = {
            "ssc_board": [
                {
                    "1": "Barisal",
                    "2": "Chittagong",
                    "3": "Comilla",
                    "4": "Dhaka",
                    "5": "Dinajpur",
                    "6": "Jessore",
                    "7": "Mymensingh",
                    "8": "Rajshahi",
                    "9": "Sylhet",
                }
            ]
        }

    return ssc_board


def existing_hsc_board_name(examtype_value):
    if examtype_value == 1:
        hsc_board = {
            "boards": [
                {
                    "1": "Barisal",
                    "2": "Chittagong",
                    "3": "Comilla",
                    "4": "Dhaka",
                    "5": "Dinajpur",
                    "6": "Jessore",
                    "7": "Mymensingh",
                    "8": "Rajshahi",
                    "9": "Sylhet",
                }
            ]
        }

    elif examtype_value == 2:
        hsc_board = {"boards": [{"10": "Edexcel", "11": "Cambridge"}]}

    elif examtype_value == 3:
        hsc_board = {
            "boards": [
                {
                    "1": "Barisal",
                    "2": "Chittagong",
                    "3": "Comilla",
                    "4": "Dhaka",
                    "5": "Dinajpur",
                    "6": "Jessore",
                    "7": "Mymensingh",
                    "8": "Rajshahi",
                    "9": "Sylhet",
                }
            ]
        }

    elif examtype_value == 4:
        hsc_board = {
            "boards": [
                {
                    "13": "BTEB"  # Bangladesh Technical Education Board
                }
            ]
        }

    return hsc_board


def get_exam_type(request):
    exam_type_value = request.GET.get("exam_type", "")
    exam_type_name = request.GET.get("exam_type_name", "")

    print("exam_type_value: ", exam_type_value)
    print("exam_type_name: ", exam_type_name)

    if exam_type_name == "secondary":
        board_type = "secondary_board"

    elif exam_type_name == "higher":
        board_type = "higher_secondary_board"

    elif exam_type_name == "higher":
        board_type = "undergraduation_board"

    else:
        board_type = "others"

    exam_type_and_board = {
        "secondary": {
            "exam_type": "secondary_board",
            "1": [
                {
                    "barisal": "Barisal",
                    "chittagong": "Chittagong",
                    "comilla": "Comilla",
                    "dhaka": "Dhaka",
                    "dinajpur": "Dinajpur",
                    "jessore": "Jessore",
                    "mymensingh": "Mymensingh",
                    "rajshahi": "Rajshahi",
                    "sylhet": "Sylhet",
                }
            ],  # SSC
            "2": [{"edexcel": "Edexcel", "Cambridge": "Cambridge"}],  # O level
            "3": [
                {
                    "barisal": "Barisal",
                    "chittagong": "Chittagong",
                    "comilla": "Comilla",
                    "dhaka": "Dhaka",
                    "dinajpur": "Dinajpur",
                    "jessore": "Jessore",
                    "mymensingh": "Mymensingh",
                    "rajshahi": "Rajshahi",
                    "sylhet": "Sylhet",
                }
            ],  # Dhakhil
            "4": [
                {
                    "barisal": "Barisal",
                    "chittagong": "Chittagong",
                    "comilla": "Comilla",
                    "dhaka": "Dhaka",
                    "dinajpur": "Dinajpur",
                    "jessore": "Jessore",
                    "mymensingh": "Mymensingh",
                    "rajshahi": "Rajshahi",
                    "sylhet": "Sylhet",
                }
            ],  # Madrashah
        },
        "higher": {
            "1": [
                {
                    "barisal": "Barisal",
                    "chittagong": "Chittagong",
                    "comilla": "Comilla",
                    "dhaka": "Dhaka",
                    "dinajpur": "Dinajpur",
                    "jessore": "Jessore",
                    "mymensingh": "Mymensingh",
                    "rajshahi": "Rajshahi",
                    "sylhet": "Sylhet",
                }
            ],  # HSC
            "2": [{"edexcel": "Edexcel", "Cambridge": "Cambridge"}],  # A Level
            "3": [
                {
                    "barisal": "Barisal",
                    "chittagong": "Chittagong",
                    "comilla": "Comilla",
                    "dhaka": "Dhaka",
                    "dinajpur": "Dinajpur",
                    "jessore": "Jessore",
                    "mymensingh": "Mymensingh",
                    "rajshahi": "Rajshahi",
                    "sylhet": "Sylhet",
                }
            ],  # Vocational
            "4": [{"bteb": "Bangladesh Technical Education Board"}],  # Diploma
        },
        "undergraduation": {
            "1": [{"ugc": "UGC"}],  # Undergraduation
        },
    }

    if exam_type_name in exam_type_and_board:
        if exam_type_value in exam_type_and_board[exam_type_name]:
            exam_board_list = exam_type_and_board[exam_type_name][exam_type_value]
            print("exam_board_dict: ", exam_board_list)

        else:
            return JsonResponse({"error": "Please fill out all the fields correctly"})

    else:
        return JsonResponse({"error": "Please fill out all the fields correctly"})

    return JsonResponse(
        {"success": True, "board_names": exam_board_list, "board_type": board_type}
    )


@login_required(login_url="login_student")
def student_profile(request):
    # Assuming each student is associated with a user
    student_user = request.user.id
    page_name = "Profile"
    page_description = "This is a top level student visa related information web portal, you can get any types of information from here. also you can take lates of visa agent information from here."
    page_keywords = "education visa consultant agent in dhaka, student visa informatin agent, student visa need, student visa consultant company, need student visa from dhaka,"

    try:
        student = Students.objects.get(id=student_user)
        results = Results.objects.filter(student_id=student.id)
        masters_degrees = MastersDegree.objects.filter(
            student_id=student_user
        ).order_by("-passing_year")[:2]
        other_certifications = OtherCertification.objects.filter(
            student_id=student_user
        )

        # Print the results details for debugging purposes
        for result in results:
            print(
                "Result Details:",
                result.id,
                result.secondary,
                result.secondary_board,
                result.secondary_result,
                result.secondary_passing_year,
            )

        # Retrieve student details
        student_details = StudentDetails.objects.filter(
            dets_regs_id=student_user
        ).first()

        if student_details:
            fav_consultant_list = student_details.dets_favconsultantlist
            consultant_count = (
                len(fav_consultant_list.split(",")) if fav_consultant_list else 0
            )
        else:
            consultant_count = 0

    except Students.DoesNotExist:
        # Handle the case where the student doesn't exist
        student = None
        results = None
        consultant_count = 0

    context = {
        "student": student,
        "results": results,
        "student_details": student_details,
        "consultant_count": consultant_count,
        "page_name": page_name,
        "masters_degrees": masters_degrees,
        "other_certifications": other_certifications,
        "page_description": page_description,
        "page_keywords": page_keywords,
    }

    return render(request, "studentinfo/student_profile.html", context)


@login_required(login_url="login_student")
def edit_student_profile(request):
    student_user = request.user.id
    page_name = "Edit Profile"
    page_description = "This is a top level student visa related information web portal, you can get any types of information from here. also you can take lates of visa agent information from here."
    page_keywords = "education visa consultant agent in dhaka, student visa informatin agent, student visa need, student visa consultant company, need student visa from dhaka,"

    try:
        # Try to get the student and related objects
        student = Students.objects.get(id=student_user)
        districts = District.objects.all()
        thanas = Thana.objects.all()
        student_details = StudentDetails.objects.filter(
            dets_regs_id=student_user
        ).first()
        results = Results.objects.filter(student_id=student.id)

        # Initialize password_form outside the if-else block
        password_form = PasswordChangeForm(request.user)

        if request.method == "POST":
            # Update student profile details
            student = Students.objects.filter(id=student_user).first()
            student.full_name = request.POST.get("full_name")
            student.email = request.POST.get("student_email")
            student.phone = request.POST.get("phone")
            district_id = request.POST.get("district_name")
            thana_id = request.POST.get("thana_name")

            district = District.objects.filter(id=district_id).first()
            thana = Thana.objects.filter(id=thana_id).first()

            if district:
                student.district = district
            if thana:
                student.thana = thana

            print("student districts: ", student.district.name)
            print("student thana: ", student.thana.name)

            now = timezone.now()
            student.updated_at = now

            student.save()

            # Update student details
            student_details, created_at = StudentDetails.objects.get_or_create(
                dets_regs_id=student_user, dets_status=1
            )

            student_details.dets_bloodgroup = request.POST.get("dets_bloodgroup")
            student_details.dets_fathername = request.POST.get("dets_fathername")
            student_details.dets_mothername = request.POST.get("dets_mothername")
            student_details.dets_nationality = request.POST.get("dets_nationality")

            dob = request.POST.get("dets_dob")
            if dob:
                student_details.dets_dob = request.POST.get("dets_dob")

            print("student user: ", student.id)

            # Handle student image upload
            if "student_image" in request.FILES:
                uploaded_image = request.FILES["student_image"]
                student_details.student_image = uploaded_image
                now = timezone.now()
                student_details.dets_updatedate = now
                student_details.save()
            now = timezone.now()
            student_details.dets_updatedate = now

            student_details.save()

            # Update result details
            for result in results:
                result.secondary_board = request.POST.get("sscBoard")
                result.secondary_result = request.POST.get("sscGPA")
                result.secondary_passing_year = request.POST.get("sscPassingYear")

                result.higher_board = request.POST.get("hscBoard")
                result.higher_result = request.POST.get("hscGPA")
                result.higher_passing_year = request.POST.get("hscPassingYear")
                now = timezone.now()
                result.updated_at = now

                result.save()

        # Render the template with the valid student details

        for district in districts:
            print("district: ", district)

        return render(
            request,
            "studentinfo/edit_student_profile.html",
            {
                "student": student,
                "student_details": student_details,
                "results": results,
                "password_form": password_form,
                "thanas": thanas,
                "districts": districts,
                "page_name": page_name,
                "page_description": page_description,
                "page_keywords": page_keywords,
            },
        )

    except Students.DoesNotExist:
        # Handle the case where the student doesn't exist
        messages.error(request, "Student profile not found.")
        return redirect("student_profile")


def change_student_password(request):
    if request.method == "POST":
        user = request.user
        password_data = json.loads(request.body)
        old_password = password_data["old_password"]
        new_password = password_data["new_password"]
        confirm_new_password = password_data["confirm_new_password"]

        print("password_data: ", password_data)

        if old_password and new_password and confirm_new_password:
            if new_password == confirm_new_password:
                if check_password(old_password, user.password):
                    user.set_password(new_password)
                else:
                    return JsonResponse({"error": "Wrong old password"})
            else:
                return JsonResponse({"error": "Passwords do not match"})
        user.save()

        return JsonResponse({"success": True})


def login_admin(request):
    if request.method == "POST":
        identifier = request.POST.get("identifier")
        password = request.POST.get("password")

        if identifier is not None and password is not None:
            # Check if the identifier is an email or phone number
            if "@" in identifier:  # Assuming email contains '@'
                user = EmailBackend().authenticate(
                    request, email=identifier, password=password, user_type=0
                )
            else:
                user = EmailBackend().authenticate(
                    request, phone=identifier, password=password, user_type=0
                )

            if user and (user.user_type == 0):
                login(request, user)

                if user.user_type == 0:
                    return redirect(
                        "root_home"
                    )  # Redirect to admin_home for user_type 0

            else:
                messages.error(request, "Invalid credentials")
        else:
            messages.error(request, "Please provide both identifier and password.")

    return render(request, "user_login/login_admin_root.html")


def check_phone_exist_user(request):
    if request.method == "POST":
        phone_number = request.POST.get("phone")

        # Check if the phone number exists in User model
        user_exists = Users.objects.filter(phone=phone_number).exists()

        # Return JSON response indicating if phone number exists in any of the models
        return JsonResponse({"exists": user_exists})
    else:
        return JsonResponse({"error": "Invalid request method"}, status=400)


def check_email_exist_user(request):
    if request.method == "POST":
        email = request.POST.get("email")

        # Check if the email exists in User model
        user_exists = Users.objects.filter(email=email).exists()

        # Return JSON response indicating if email exists in any of the models
        return JsonResponse({"exists": user_exists})
    else:
        return JsonResponse({"error": "Invalid request method"}, status=400)


def check_phone_exist_student(request):
    if request.method == "POST":
        phone_number = request.POST.get("phone")

        # Check if the phone number exists in User model
        student_exists = Students.objects.filter(phone=phone_number).exists()

        # Return JSON response indicating if phone number exists in any of the models
        return JsonResponse({"exists": student_exists})
    else:
        return JsonResponse({"error": "Invalid request method"}, status=400)


@login_required
def check_email_exist_student(request):
    if request.method == "POST":
        email = request.POST.get("email")

        # Check if the email exists in Students model
        students_email_exists = Students.objects.filter(email=email).exists()

        # Return JSON response indicating if email exists in any of the models
        return JsonResponse({students_email_exists})
    else:
        return JsonResponse({"error": "Invalid request method"}, status=400)


def custom_404_view(request, exception):
    # Handle 404 errors here
    return render(request, "error.html", status=404)


def destroy_session(request):
    # request.session.flush()
    del request.session["next_page"]
    del request.session["last_activity_time"]
    request.session.modified = True

    return JsonResponse({"success": True})


def meta(request):
    # Your view logic here

    page_description = "This is a top level student visa related information web portal, you can get any types of information from here. also you can take lates of visa agent information from here."
    page_keywords = "education visa consultant agent in dhaka, student visa informatin agent, student visa need, student visa consultant company, need student visa from dhaka,"

    context = {"page_description": page_description, "page_keywords": page_keywords}

    return render(request, "base.html", context)


def address_view(request):
    page_name = "Contact Us | Address "
    page_description = "This is a top level student visa related information web portal, you can get any types of information from here. also you can take lates of visa agent information from here."
    page_keywords = "education visa consultant agent in dhaka, student visa informatin agent, student visa need, student visa consultant company, need student visa from dhaka,"

    # Get the id of the user with user_type 0 (Root)
    root_user = CustomUser.objects.filter(user_type=0).order_by("-id").first()

    if root_user:
        # Filter addresses based on the matching consultant_id and root user's id
        addresses = Addresses.objects.filter(consultant_id=root_user.id)

        # Get the last address based on created_at field
        last_address = addresses.order_by("-created_at").first()

        if last_address:
            return render(
                request,
                "address.html",
                {
                    "addresses": [last_address],
                    "page_name": page_name,
                    "page_description": page_description,
                    "page_keywords": page_keywords,
                },
            )
        else:
            # If no matching address found, handle this case as per your requirement
            return render(
                request, "error.html", {"message": "No matching address found"}
            )
    else:
        # If no root user found, handle this case as per your requirement
        return render(request, "error.html", {"message": "No root user found"})


def map_view(request):
    consultants = CustomUser.objects.filter(user_type=0)
    consultant_maps = []
    page_name = "Contact Us | Maps "
    page_description = "This is a top level student visa related information web portal, you can get any types of information from here. also you can take lates of visa agent information from here."
    page_keywords = "education visa consultant agent in dhaka, student visa informatin agent, student visa need, student visa consultant company, need student visa from dhaka,"

    for consultant in consultants:
        maps = Maps.objects.filter(consultant_id=consultant.id)
        for map in maps:
            consultant_maps.append(
                {"consultant": consultant, "map_location": map.map_location}
            )

    return render(
        request,
        "map.html",
        {
            "consultant_maps": consultant_maps,
            "page_name": page_name,
            "page_description": page_description,
            "page_keywords": page_keywords,
        },
    )


def feedback_view(request):
    category_choices = Message.CATEGORY_CHOICES
    page_name = "Contact Us | Feedback"
    page_description = "This is a top level student visa related information web portal, you can get any types of information from here. also you can take lates of visa agent information from here."
    page_keywords = "education visa consultant agent in dhaka, student visa informatin agent, student visa need, student visa consultant company, need student visa from dhaka,"

    if request.method == "POST":
        # Extract data from the request
        category = request.POST.get("category")
        email = request.POST.get("email")
        name = request.POST.get("name")
        phonenumber = request.POST.get("phonenumber")
        subject = request.POST.get("subject")
        message_text = request.POST.get("message")
        captcha_token = request.POST.get("g-recaptcha-response")

        # Perform reCAPTCHA verification
        cap_url = "https://www.google.com/recaptcha/api/siteverify"
        cap_secret = "6LcxvG8pAAAAAIaMvcT9M_ys9A7ytKR1UCIZFvKW"
        cap_data = {"secret": cap_secret, "response": captcha_token}
        cap_server_response = requests.post(url=cap_url, data=cap_data)
        cap_json = json.loads(cap_server_response.text)

        if cap_json.get("success", False):
            try:
                # Create and save a Message instance
                message = Message.objects.create(
                    category=category,
                    email=email,
                    name=name,
                    phonenumber=phonenumber,
                    subject=subject,
                    message=message_text,
                    created_at=timezone.now(),
                )

                # Send email notification
                email_subject = f"New message received: {subject}"
                email_message = f"Name: {name}\nEmail: {email}\nPhone Number: {phonenumber}\nMessage: {message_text}"
                sender_email = settings.EMAIL_HOST_USER
                recipient_email = (
                    settings.EMAIL_HOST_USER
                )  # Send email to configured email address
                send_mail(email_subject, email_message, sender_email, [recipient_email])

                messages.success(request, "Message submitted successfully!")
            except Exception as e:
                messages.error(request, f"An error occurred: {str(e)}")
        else:
            messages.error(request, "Please complete the reCAPTCHA verification.")

        return redirect("feedback-home")

    return render(
        request,
        "feedback_home.html",
        {
            "page_name": page_name,
            "page_description": page_description,
            "page_keywords": page_keywords,
            "category_choices": category_choices,
        },
    )


def service_detail(request, slug):
    service = get_object_or_404(VisaService, slug=slug)
    return render(request, "service_detail.html", {"service": service})
