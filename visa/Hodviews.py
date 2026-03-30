from django.shortcuts import render,redirect
from .models import *
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import check_password
from datetime import datetime
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponse
from .serializers import ModelJSONEncoder
from django.db.models import Sum
from django.shortcuts import render, redirect
from .models import Maps, ConsultantDetails
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.db.models import Avg, F, ExpressionWrapper, fields
from django.db.models import F, Q
from django.db.models import Subquery, OuterRef
from django.db.models.functions import ExtractMonth, ExtractYear
from django.db.models import Count, F
from django.db.models import Sum, F, Case, When, Value, FloatField
from django.db.models.functions import TruncMonth
from django.contrib import messages
from django.http import HttpResponseServerError
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.files.storage import default_storage

def is_consultant(user):
    return user.is_authenticated and user.user_type == 1


def get_logged_in_consultant(user):
    return get_object_or_404(Users, consultant_user_id=user.id, user_role=5)


def get_consultant_details_instance(consultant, create=False):
    consultant_details = ConsultantDetails.objects.filter(
        consultant_id=consultant.id
    ).first()

    if consultant_details is None and consultant.consultant_user_id:
        consultant_details = ConsultantDetails.objects.filter(
            consultant_id=consultant.consultant_user_id
        ).first()
        if consultant_details:
            consultant_details.consultant_id = consultant.id
            consultant_details.save(update_fields=["consultant_id"])

    if consultant_details is None and create:
        consultant_details = ConsultantDetails.objects.create(
            consultant_id=consultant.id
        )

    return consultant_details


@login_required(login_url='login_user')
@user_passes_test(is_consultant, login_url='login_user')
def consultant_home(request):
    # Assuming consultant_id is related to the user
    consultant = get_logged_in_consultant(request.user)
    consultant_id = consultant.id

  

    # Calculate total credit and debit for the consultant
    total_credit = Balances.objects.filter(acc_pay_to=consultant_id).aggregate(Sum('acc_credit'))['acc_credit__sum'] or 0.0
    total_debit = Balances.objects.filter(acc_paid_by=consultant_id).aggregate(Sum('acc_debit'))['acc_debit__sum'] or 0.0
    print('total_debit:', total_debit)
    
    # Calculate total balance
    total_balance = total_credit - total_debit
    print("total_balance:", total_balance)

    # Count the number of students for the consultant
    total_students = Levels.objects.filter(consultant_id=consultant_id, status=1).count()
    total_students_all =  Students.objects.count()
    average_students = total_students_all / total_students if total_students != 0 else 0
    new_students_count = Students.objects.filter(
        ~Q(id__in=Subquery(Levels.objects.filter(consultant_id=OuterRef('id')).values('student_id')))
    ).count()
    print('new_students_count:', new_students_count)
    return render(request, 'Hodviews/index.html', {'total_balance': total_balance,  'total_students': total_students,'total_debit':total_debit,'average_students':average_students,'new_students_count':new_students_count,'consultant':consultant })









def new_students_view(request):
    # Fetch the last six newly added students
    latest_students = Students.objects.order_by('-id')[:6]

    # Prepare data to be returned in JSON format
    new_students_data = []
    for student in latest_students:
        # Fetch the student's latest result
        latest_result = Results.objects.filter(student_id=student.id).order_by('-created_at').first()

        # Fetch student level
        try:
            level = Levels.objects.get(student_id=student.id)
            student_level = None
            if level.level_1 is not None:
                student_level = 1
            elif level.level_2 is not None:
                student_level = 2
            elif level.level_3 is not None:
                student_level = 3
            elif level.level_4 is not None:
                student_level = 4
            elif level.level_5 is not None:
                student_level = 5
        except Levels.DoesNotExist:
            student_level = None
        
        # Fetch the countries associated with the student
        countries = [country.country_name for country in student.countries.all()]

        student_data = {
            'name': student.full_name,
            'countries': countries,
            'gender': student.gender,
            'secondary_result': latest_result.secondary_result if latest_result else None,
            'higher_result': latest_result.higher_result if latest_result else None,
            'level': student_level,
            # Add more fields as needed
        }
        new_students_data.append(student_data)

    # Return data in JSON response
    return JsonResponse({'new_students': new_students_data})
@login_required(login_url='login_user')
@user_passes_test(is_consultant, login_url='login_user')
def monthly_balance_chart(request):
    consultant_id = get_logged_in_consultant(request.user).id

    # Get total credit and debit per month
    monthly_data = Balances.objects.filter(
        Q(acc_pay_to=consultant_id) | Q(acc_paid_by=consultant_id)
    ).annotate(month=TruncMonth('created_at')).values('month').annotate(
        total_credit=Sum('acc_credit'),
        total_debit=Sum('acc_debit')
    ).order_by('month')

    # Prepare data for chart
    labels = [entry['month'].strftime('%B %Y') for entry in monthly_data]
    credit_data = [entry['total_credit'] or 0.0 for entry in monthly_data]
    debit_data = [entry['total_debit'] or 0.0 for entry in monthly_data]

    # Prepare data to pass to the template
    chart_data = {
        'labels': labels,
        'credit_data': credit_data,
        'debit_data': debit_data,
    }

    return JsonResponse(chart_data)

@login_required(login_url='login_user')
@user_passes_test(is_consultant, login_url='login_user')
def consultant_ratings_json(request):
    consultant_id = get_logged_in_consultant(request.user).id

    ratings = Review.objects.filter(consultant=consultant_id).values_list('rating', flat=True)
    average_rating = sum(ratings) / len(ratings) if ratings else 0

    # Set the highest rating to 5
    highest_rating = 5

    # Send the data in the format expected by the chart
    data = {
        'labels': ['Average Rating', 'Highest Rating'],
        'values': [average_rating, highest_rating],
    }

    return JsonResponse({'ratings_data': data})
    
    
@login_required(login_url='login_user')
@user_passes_test(is_consultant, login_url='login_user')
def consultant_gallery(request):
    error_message = None
    images = None
    consultant = get_logged_in_consultant(request.user)
    consultant_id = consultant.id

    if request.method == 'POST':
        image = request.FILES.get('image')
        caption = request.POST.get('caption')
        
        # Check if the consultant already has 12 images
        image_count = ConsultantImages.objects.filter(consultant_id=consultant_id).count()
        if image_count >= 12:
            error_message = "You can only upload a maximum of 12 images."
        elif image and caption and consultant_id:
            # Check if caption length exceeds 30 characters
            if len(caption) > 30:
                error_message = "Caption should not exceed 30 characters."
            else:
                ConsultantImages.objects.create(
                    image=image,
                    caption=caption,
                    consultant_id=consultant_id,
                    created_at=timezone.now(),
                    updated_at=timezone.now()
                )
                return redirect('consultant_gallery')  # Redirect to the same page after successful submission
        else:
            error_message = "Please provide all required information."

    # Fetch images regardless of whether there's an error or not
    images = ConsultantImages.objects.filter(consultant_id=consultant_id)

    return render(request, 'Hodviews/gallery.html', {'images': images, 'error_message': error_message})
        
        
        
@login_required(login_url='login_user')
def delete_gallery(request, image_id):
    consultant_id = get_logged_in_consultant(request.user).id
    image_to_delete = get_object_or_404(ConsultantImages, id=image_id, consultant_id=consultant_id)

    # Get the path of the image file
    if image_to_delete.image:
        image_path = os.path.join(settings.MEDIA_ROOT, image_to_delete.image.name)

        # Delete the image file if it exists
        if os.path.exists(image_path):
            os.remove(image_path)

    # Delete the image object from the database
    image_to_delete.delete()

    return JsonResponse({'message': 'Image deleted successfully'}, status=200)
        
        
@login_required(login_url='login_user')
@user_passes_test(is_consultant, login_url='login_user')
def consultant_profile(request):
    if request.user.is_authenticated:
        print('user: ', request.user.email)
        user_id = request.user.id
        user = Users.objects.get(consultant_user_id=user_id)
        print('est. date: ', user.est_date)
        context = {
            'user': user,
        }
    return render(request, 'Hodviews/consultant_profile.html', context)

@login_required(login_url='login_user')
def save_consultant_profile(request, user_id):
    if request.method == 'POST' and request.user.is_authenticated:
        user = request.user
        if user.id == int(user_id):
            company_name = request.POST.get('company_name')
            full_name = request.POST.get('full_name')
            phone = request.POST.get('phone')
            land_phone = request.POST.get('land_phone')
            fax_no = request.POST.get('fax_no')
            date_str = request.POST.get('est_date')
            address = request.POST.get('address')
            website = request.POST.get('website')
            experience= request.POST.get('experience')
            designation= request.POST.get('designation')
            about = request.POST.get('consultant_about')
            old_password = request.POST.get('old_password')
            new_password = request.POST.get('new_password')
            confirm_password = request.POST.get('confirm_password')
            consultant_img = request.FILES.get('consultant_img')
            print('company_name: ', company_name)
            print('full_name: ', full_name)
            print('phone: ', phone)
            print('land_phone: ', land_phone)
            print('fax_no: ', fax_no)
            print('est_date: ', date_str)
            print('address: ', address)
            print('experiance: ', experience)
            print('website: ', website)
            print('about: ', about)
            print('consultant_img: ', consultant_img)
            consultant_id = int(user_id)
            consultant = Users.objects.get(consultant_user_id=consultant_id)
            if company_name and full_name and phone and address:
                
                consultant.company_name = company_name
                consultant.full_name = full_name
                consultant.phone = phone
                consultant.address = address
                consultant.website = website
                if consultant.consultant_img and consultant_img:
                # Delete the existing image
                    img_path = consultant.consultant_img.path
                    default_storage.delete(img_path)


                if website:
                    consultant.website = website
                if about:
                    consultant.about = about
                if land_phone:
                    consultant.land_phone = land_phone
                if fax_no:
                    consultant.fax_no = fax_no
                if consultant_img:
                    consultant.consultant_img = consultant_img

                if date_str:
                    try:
                        est_date = datetime.strptime(date_str, "%B %d, %Y").strftime("%Y-%m-%d")
                        consultant.est_date = est_date
                    except:
                        try:
                            est_date = datetime.strptime(date_str, "%b. %d, %Y").strftime("%Y-%m-%d")
                            consultant.est_date = est_date
                        except:
                            try:
                                est_date = date_str
                                consultant.est_date = est_date
                            except:
                                return JsonResponse({'error': 'Error parsing date'})
                            
                if old_password and  new_password and confirm_password:
                    if new_password == confirm_password:
                        if check_password(old_password, user.password):
                            user.set_password(new_password)
                        else:
                            return JsonResponse({'error': 'Wrong old password'})
                    else:
                        return JsonResponse({'error': 'Passwords do not match'})
                user.save()
                consultant.save()
                consultant_details = get_consultant_details_instance(consultant, create=True)

                if experience:
                    consultant_details.experience = experience
                
                if designation:
                    consultant_details.consultant_designation=designation
                consultant_details.save()

                print("consultant_details:")
                return JsonResponse({'success': True})
            else:
                return JsonResponse({'error': 'Please fill up all the required fields'})
        else:
            return JsonResponse({'error': 'Cannot update your account information due to security reasons'})
    else:
        return JsonResponse({'error': 'Invalid request'})
    


from django.conf import settings
from django.core.files.images import get_image_dimensions
from PIL import Image
import io

@login_required(login_url='login_user')
@user_passes_test(is_consultant, login_url='login_user')
def consultant_logo(request):
    if request.user.is_authenticated:
        user = request.user
        consultant = get_logged_in_consultant(user)
        consultant_details = get_consultant_details_instance(consultant, create=True)

        if request.method == 'POST':
            logo = request.FILES.get('logo')
            if logo:
                # Check file size
                if logo.size > settings.MAXIMUM_UPLOAD_SIZE:
                    # Resize the image
                    image_temporary = Image.open(logo)
                    output_io_stream = io.BytesIO()
                    # Resize the image while maintaining aspect ratio
                    image_temporary.thumbnail((150, 150))  # Adjust size as needed
                    image_temporary.save(output_io_stream, format='JPEG')
                    output_io_stream.seek(0)

                    # Save the resized image
                    consultant_details.consultant_logo.save(generate_filename(consultant.id, consultant.company_name), output_io_stream, save=False)
                    consultant_details.save()

                    return JsonResponse({'success': True})
                else:
                    consultant_details.consultant_logo.save(generate_filename(consultant.id, consultant.company_name), logo, save=True)

                    return JsonResponse({'success': True})

        context = {
            'consultant': consultant,
            'consultant_details': consultant_details,
        }
        return render(request, 'Hodviews/consultant_logo.html', context)

def generate_filename(consultant_id, company_name):
    # Generate a unique filename for the logo
    ext = '.jpg'  # Assuming it's JPEG format, you may adjust accordingly
    filename = f"{consultant_id}-{slugify(company_name)}_logo{ext}"
    return filename

def save_logo(request):
    if request.method == 'POST':
        if request.user.is_authenticated:
            consultant_logo = request.FILES.get('logo')
            user = request.user
            consultant = get_logged_in_consultant(user)
            consultant_details = get_consultant_details_instance(consultant, create=True)

            # Check if there is an existing logo
            if consultant_details.consultant_logo:
                # Get the path of the existing logo file
                existing_logo_path = os.path.join(settings.MEDIA_ROOT, consultant_details.consultant_logo.name)
                
                # Check if the file exists before attempting to remove it
                if os.path.exists(existing_logo_path):
                    # Remove the existing logo file
                    os.remove(existing_logo_path)
            
            # Save the new logo
            consultant_details.consultant_logo.save(generate_filename(consultant.id, consultant.company_name), consultant_logo, save=True)
            
            return JsonResponse({'success': True})
        else:
            return JsonResponse({'error': 'Unauthorized User'})


@login_required(login_url='login_user')
@user_passes_test(is_consultant, login_url='login_user')
def consultant_requirement(request):
    consultant = get_logged_in_consultant(request.user)
    consultant_details = get_consultant_details_instance(consultant, create=True)
    created = consultant_details.created_at is None

    if request.method == 'POST':
        consultant_requirement = request.POST.get('consultant_requirement')
        consultant_requirement_image = request.FILES.get('consultant_requirement_image')

        if consultant_details is not None:
            consultant_details.consultant_requirement = consultant_requirement

            # If consultant ID has changed, update the filenames accordingly
            if consultant_details.consultant_id != consultant.id:
                consultant_details.consultant_id = consultant.id
                # Update consultant_requirement_image filename
                if consultant_details.consultant_requirement_image:
                    old_filename = consultant_details.consultant_requirement_image.name
                    old_filename_parts = old_filename.split('-')
                    new_filename = f"{consultant.id}-{slugify(consultant.company_name)}_req-{old_filename_parts[-1]}"
                    consultant_details.consultant_requirement_image.name = new_filename

            # Delete the old image if it exists
            if consultant_details.consultant_requirement_image and consultant_requirement_image:
                # Get the path of the existing image file
                existing_image_path = os.path.join(settings.MEDIA_ROOT, consultant_details.consultant_requirement_image.name)
                # Check if the file exists before attempting to remove it
                if os.path.exists(existing_image_path):
                    # Remove the existing image file
                    os.remove(existing_image_path)

            if consultant_requirement_image:
                consultant_details.consultant_requirement_image = consultant_requirement_image

            consultant_details.status = consultant_details.status if consultant_details.status is not None else 1
            consultant_details.created_at = timezone.now()
            consultant_details.updated_at = timezone.now()
            consultant_details.save()

            messages.success(request, 'Consultant requirement updated successfully.')
            return redirect('consultant_requirement')

        messages.error(request, 'Error updating consultant requirement.')

    return render(request, 'Hodviews/consultant_requirement.html', {'consultant_details': consultant_details, 'created': created})


@login_required(login_url='login_user')
@user_passes_test(is_consultant, login_url='login_user')
def consultant_country(request):
    consultant = get_logged_in_consultant(request.user)
    consultant_id = consultant.id
    consultant_details = get_consultant_details_instance(consultant, create=True)

    all_countries = Countries.objects.all()

    saved_country_ids = consultant_details.consultant_countries.values_list('country_id', flat=True)

    saved_countries = Countries.objects.filter(country_id__in=saved_country_ids)

    available_countries = all_countries.exclude(country_id__in=saved_country_ids)

    if request.method == 'POST':
        consultant_country_id = request.POST.get('consultant_countries')
        if consultant_country_id:
            selected_country = Countries.objects.get(country_id=consultant_country_id)
            print('selected_country:', selected_country)

            consultant_details.consultant_countries.add(selected_country)

            return redirect('consultant_country')  

    return render(request, 'Hodviews/consultant_country.html', {'saved_countries': saved_countries, 'available_countries': available_countries})






def delete_country(request):
    # Check if the request is a POST request and an Ajax request
    if request.method == 'POST' and request.headers.get('x-requested-with') == 'XMLHttpRequest':
        # Get the current user's consultant ID
        consultant = get_logged_in_consultant(request.user)
        consultant_id = consultant.id
        # Get the country name from the POST data
        country_name = request.POST.get('country_name')
        try:
            # Get the ConsultantDetails instance for the current consultant
            consultant_details = get_consultant_details_instance(consultant, create=True)
            # Get the corresponding country instance
            country = get_object_or_404(Countries, country_name=country_name)
            # Remove the selected country from the consultant_details
            consultant_details.consultant_countries.remove(country)
            # Return a JSON response indicating success
            return JsonResponse({'success': True})
        except ConsultantDetails.DoesNotExist:
            # Return a JSON response indicating failure (ConsultantDetails not found)
            return JsonResponse({'success': False, 'error': 'ConsultantDetails not found'})
        except Countries.DoesNotExist:
            # Return a JSON response indicating failure (Country not found)
            return JsonResponse({'success': False, 'error': 'Country not found'})
        except Exception as e:
            # Return a JSON response indicating failure with the specific error message
            return JsonResponse({'success': False, 'error': f'An error occurred: {str(e)}'})
    # Return a JSON response indicating failure for invalid requests
    return JsonResponse({'success': False, 'error': 'Invalid request'})




@login_required(login_url='login_user')
@user_passes_test(is_consultant, login_url='login_user')
def consultant_scholarship(request):
    success_message = None
    countries = Countries.objects.all()

    if request.method == 'POST':
        schp_description = request.POST.get('schp_description')
        apply_process = request.POST.get('apply_process')
        
        # Assuming consultant_id should be set to the currently logged-in user's ID
        consultant_id = get_logged_in_consultant(request.user).id
        country_id = request.POST.get('country_id')
        country_instance = Countries.objects.get(country_id=country_id)

        # Current timestamp for created_at and updated_at
        now = timezone.now()

        try:
            # Create a new scholarship instance
            scholarship = ScholarShips.objects.create(
                schp_description=schp_description,
                apply_process=apply_process,
                consultant_id=consultant_id,
                created_at=now,
                updated_at=now,
                country_name=country_instance,
            )

            # Set the success message
            success_message = "Scholarship added successfully."

        except Exception as e:
            
            return render(request, 'Hodviews/consultant_scholarship.html', {'error_message': f"Error: {e}"})

    # Render a form or any other relevant content for GET requests
    return render(request, 'Hodviews/consultant_scholarship.html', {'success_message': success_message,  'countries': countries})






def consultant_map(request):
    success_message = None
    error_message = None
    existing_map_location = None

    if request.method == 'POST':
        map_location = request.POST.get('map_location')
        consultant = get_logged_in_consultant(request.user)
        consultant_id = consultant.id
        now = timezone.now()

        try:
            map_instance = Maps.objects.get(consultant_id=consultant_id)
            existing_map_location = map_instance.map_location

            map_instance.map_location = map_location
            map_instance.updated_at = now
            map_instance.save()

            success_message = "Map updated successfully."

        except Maps.DoesNotExist:
            map_instance = Maps.objects.create(
                map_location=map_location,
                consultant_id=consultant_id,
                created_at=now,
                updated_at=now
            )

            consultant_details = get_consultant_details_instance(consultant, create=True)
            consultant_details.consultant_maplocation = map_instance.map_location
            consultant_details.save()

            success_message = "Map added successfully."

        except ConsultantDetails.DoesNotExist:
            error_message = "Error: ConsultantDetails not found for the given consultant_id."
        
        except Exception as e:
            error_message = f"Error: {str(e)}"

    else:
        consultant_id = get_logged_in_consultant(request.user).id
        try:
            map_instance = Maps.objects.get(consultant_id=consultant_id)
            existing_map_location = map_instance.map_location
        except Maps.DoesNotExist:
            pass

    return render(request, 'Hodviews/consultant_map.html', {
        'success_message': success_message,
        'error_message': error_message,
        'existing_map_location': existing_map_location
    })
def linkpage(request):
    return render(request,'Hodviews/linkpage.html')



from django.shortcuts import render, redirect
from django.utils import timezone
from .models import Colors
@login_required(login_url='login_user')
@user_passes_test(is_consultant, login_url='login_user')
def consultant_color(request):
    consultant_id = get_logged_in_consultant(request.user).id

    try:
        consultant_colors = Colors.objects.get(consultant_id=consultant_id)
    except Colors.DoesNotExist:
        consultant_colors = None

    success_message = None
    error_message = None

    if request.method == 'POST':
        header_color = request.POST.get('header_color')
        content_color = request.POST.get('content_color')
        footer_color = request.POST.get('footer_color')

        print("header_color:", header_color)
        print("content_color:", content_color)
        print("footer_color:", footer_color)

        if header_color is not None and content_color is not None and footer_color is not None:
            now = timezone.now()

            try:
                if consultant_colors:
                    consultant_colors.header_color = header_color
                    consultant_colors.content_color = content_color
                    consultant_colors.footer_color = footer_color
                    consultant_colors.updated_at = now
                    consultant_colors.save()
                else:
                    Colors.objects.create(
                        header_color=header_color,
                        content_color=content_color,
                        footer_color=footer_color,
                        consultant_id=consultant_id,
                        created_at=now,
                        updated_at=now
                    )

                success_message = "Color settings successfully saved."
            except Exception as e:
                error_message = f"Error saving colors: {str(e)}"
                print(error_message)
                return HttpResponseServerError(error_message)

    return render(request, 'Hodviews/consultant_color.html', {
        'consultant_colors': consultant_colors,
        'success_message': success_message,
        'error_message': error_message
    })

@login_required(login_url='login_user')
@user_passes_test(is_consultant, login_url='login_user')
def consultant_intro(request):
    # Initialize variables
    success_message = None
    consultant = None
    customize = None

    if request.method == 'POST':
        # Retrieve form data from the POST request
        consultant_bio = request.POST.get('consultant_bio')
        consultant_intro = request.POST.get('consultant_intro')
        consultant_description = request.POST.get('consultant_description')

        # Get the currently logged-in user
        consultant_user = request.user
        consultant_profile = get_logged_in_consultant(consultant_user)
        consultant_id = consultant_profile.id

        # Current timestamp for created_at and updated_at
        now = timezone.now()

        try:
            # Attempt to retrieve the existing consultant details
            consultant = get_consultant_details_instance(consultant_profile, create=True)
            consultant.consultant_bio = consultant_bio
            consultant.consultant_intro = consultant_intro
            consultant.consultant_description = consultant_description
            consultant.updated_at = now
            consultant.save()

            # Update or create Customizes instance based on consultant_id
            customize, created = Customizes.objects.update_or_create(
                consultant_id=consultant_id,
                defaults={
                    'description': consultant_description,
                    'image': request.FILES.get('image'),  # Assuming the file input name is 'image'
                    'status': 1
                }
            )

            success_message = "Consultant details updated successfully."

        except ConsultantDetails.DoesNotExist:
            pass

    # Retrieve the latest consultant details for display
    consultant_profile = get_logged_in_consultant(request.user)
    consultant = get_consultant_details_instance(consultant_profile, create=True)
    customize = Customizes.objects.filter(consultant_id=consultant_profile.id).first()


    # Render the template with relevant context
    return render(request, 'Hodviews/consultant_intro.html', {
        'success_message': success_message,
        'consultant': consultant,
        'customize': customize
    })
    
    
@login_required(login_url='login_user')
@user_passes_test(is_consultant, login_url='login_user')
def student_list(request):
    students = Students.objects.filter(status=2).order_by('full_name')
    student_details = StudentDetails.objects.all()

    student_levels = []

    # Retrieve "My Lead" data using the update_my_lead view
    my_lead_data = update_my_lead(request)

    consultant_id = get_logged_in_consultant(request.user).id
    viewed_students = [level.student_id for level in Levels.objects.filter(consultant_id=consultant_id)]

    for student, student_detail in zip(students, student_details):
        # Check if the student has been viewed by the consultant
        if student.id in viewed_students:
            # If viewed, add to 'My Lead' section
            is_favorite = False
            if student_detail.dets_favconsultantlist and str(consultant_id) in student_detail.dets_favconsultantlist.split(','):
                is_favorite = True

            student_levels.append({'student': student, 'level': None, 'is_favorite': is_favorite, 'student_detail': student_detail})
        else:
            # If not viewed, determine the lead level and add to the lead section
            consultants_viewed_count = Levels.objects.filter(student_id=student.id).order_by('-created_at').first()

            if consultants_viewed_count is None:
                level = 1
            elif consultants_viewed_count.level_1 is not None:
                level = 2
            elif consultants_viewed_count.level_2 is not None:
                level = 3
            elif consultants_viewed_count.level_3 is not None:
                level = 4
            else:
                level = 5

            is_favorite = False
            if student_detail.dets_favconsultantlist and str(consultant_id) in student_detail.dets_favconsultantlist.split(','):
                is_favorite = True

            student_levels.append({'student': student, 'level': level, 'is_favorite': is_favorite, 'student_detail': student_detail})

    context = {
        'student_levels': student_levels,
        'my_lead_included': my_lead_data,  # Include "My Lead" data in the context
    }

    return render(request, 'Hodviews/student_list.html', context)
    
    
@login_required(login_url='login_user')
@user_passes_test(is_consultant, login_url='login_user')
def update_my_lead(request):
    consultant_id = get_logged_in_consultant(request.user).id
    student_levels = Levels.objects.filter(consultant_id=consultant_id)

    data = []
    for student_level in student_levels:
        for i in range(1, 6):
            student_id_field = getattr(student_level, f'level_{i}', None)
            if student_id_field is not None:
                student = Students.objects.get(id=student_id_field)
                result = Results.objects.filter(student_id=student.id).first()  # Assuming one result per student
                
                if result:
                    secondary_certificate_copy = result.secondary_certificate_copy.url if result.secondary_certificate_copy else None
                    higher_certificate_copy = result.higher_certificate_copy.url if result.higher_certificate_copy else None
                    
                data.append({
                    'id': student.id,
                    'full_name': student.full_name,
                    'email': student.email,
                    'phone': student.phone,
                    'gender': student.gender,
                    'address': student.address,
                    'country_name': student.countries.first().country_name if student.countries.first() else 'N/A',
                    'higher_certificate_copy': higher_certificate_copy,
                    'secondary_certificate_copy': secondary_certificate_copy,
                })

    return data


def get_consultant_balance(consultant_id):

    total_credit = Balances.objects.filter(acc_pay_to=consultant_id).aggregate(Sum('acc_credit'))['acc_credit__sum'] or 0.0
    total_debit = Balances.objects.filter(acc_paid_by=consultant_id).aggregate(Sum('acc_debit'))['acc_debit__sum'] or 0.0
    current_balance = total_credit - total_debit
    return current_balance
    
    
@login_required(login_url='login_user')
@user_passes_test(is_consultant, login_url='login_user')
def view_students_by_consultant(request, lead, student_id):
    # Get the student object based on the provided student_id
    student = get_object_or_404(Students, id=student_id)
    student_lead = lead

    # Get the student details
    student_details = StudentDetails.objects.filter(dets_regs_id=student_id).first()
    student_results = Results.objects.filter(student_id=student_id).first()

    # Prepare student data
    student_user_id = student.student_user.id if student.student_user else None

    student_countries = student.countries.all().values_list('country_name', flat=True)
    print('student_countries: ', student_countries)
    student_data = {
        "id": student.id,
        "full_name": student.full_name,
        "student_user": student_user_id,
        "email": student.email,
        "phone": student.phone,
        "address": student.address,
        "gender": student.gender,
        "student_countries": list(student_countries),
        "lead": lead
    }

    # print('student_results.higher_certificate_copy.url: ', student_results.higher_certificate_copy.url)

    # Prepare context for JSON response
    context = {
        'lead': lead,
        'student_level': {'student': student_data, 'level': lead},
        'student_details': student_details,
        'student_results': student_results,
        # 'secondary_certificate_copy': student_results.secondary_certificate_copy.url if student_results.secondary_certificate_copy else None,
        # 'higher_certificate_copy': student_results.higher_certificate_copy.url if student_results.higher_certificate_copy else None
    }

    if student_results:
        context['secondary_certificate_copy'] = student_results.secondary_certificate_copy.url if student_results.secondary_certificate_copy else None
        context['higher_certificate_copy'] = student_results.higher_certificate_copy.url if student_results.higher_certificate_copy else None
        context['undergraduation_certificate_copy'] = student_results.undergraduation_certificate_copy.url if student_results.undergraduation_certificate_copy else None

    # Return JSON response
    return JsonResponse(context, encoder=ModelJSONEncoder)



@login_required(login_url='login_user')
@user_passes_test(is_consultant, login_url='login_user')
def update_balance(request, lead, student_id):
    # Get the student object based on the provided student_id
    student = get_object_or_404(Students, id=student_id)
    print('student sajal:', student.id)

    # Get the student details
    student_details = StudentDetails.objects.filter(dets_regs_id=student_id).first()

    if student:
        result = Results.objects.filter(student_id=student.id).first()
        # result_serialize = serialize('json', result)
        print('result_serialize: ', result)

    # Get the rates for the current consultant
    consultant_id = get_logged_in_consultant(request.user).id
    rates_data = Rates.objects.filter(rate_added_to=consultant_id).first()
    if not rates_data:
        return JsonResponse({"error": "Please Contact With Administration."})

    # Determine the rate based on the lead
    if lead == 1:
        rate = rates_data.first_rate
    elif lead == 2:
        rate = rates_data.second_rate
    elif lead == 3:
        rate = rates_data.third_rate
    elif lead == 4:
        rate = rates_data.four_rate
    elif lead == 5:
        rate = rates_data.five_rate
    else:
        rate = 0.0

    # Check if there is sufficient balance
    current_balance = get_consultant_balance(consultant_id)

    level_str = f"level_{lead}"
    student_level = Levels.objects.filter(student_id=student.id, **{level_str: student.id}).first()

    if current_balance < rate:
        return JsonResponse({"error": "Insufficient balance."})
    
    elif student_level is not None:
        return JsonResponse({"error": "This Student Profile has already been viewed by another Consultant. You may find this student's information in another 'Lead'"})

    else:
        # Deduct the rate from the balance
        balance = Balances(
            acc_paid_by=consultant_id,
            acc_pay_to=student_id,
            acc_debit=rate,  # Deduct the rate
            created_at=timezone.now(),
            updated_at=timezone.now(),
        )
        balance.save()

        # Create a new Levels object
        level_model = Levels(
            balance_id=balance.id,
            student_id=student.id,
            consultant_id=consultant_id,
            status=1,
            created_at=timezone.now(),
            updated_at=timezone.now(),
        )

        # Set the level of the student with student id in the corresponding level
        setattr(level_model, f'level_{lead}', student.id)
        level_model.save()

        # Prepare student data
        student_user_id = student.student_user.id if student.student_user else None
        student_countries = student.countries.all().values_list('country_name', flat=True)

        countries_str = ', '.join(student_countries)

        print('Student countries', student_countries)
        student_image_url = student_details.student_image.url if student_details and student_details.student_image else None

        result = Results.objects.filter(student_id=student_id).first()
        masters_degrees = MastersDegree.objects.filter(student_id=student_id).order_by('-passing_year')[:2]
        other_certifications = OtherCertification.objects.filter(student_id=student_id).order_by('-passing_year')

        exam_type = {}

        # Mapping for secondary
        secondary_map = {
            1: 'SSC',
            2: 'O Level',
            3: 'Dhakhil'
        }

        # Mapping for higher
        higher_map = {
            1: 'HSC',
            2: 'A Level',
            3: 'Vocational'
        }

        undergraduation_map = {
            1: 'Undergraduation'
        }

        master_degrees_dict = {
            'masters': {}
        }
        no_of_masters_degrees = len(masters_degrees)

        for index, master_degree in enumerate(masters_degrees):
            master_str = f"master_degree_{index + 1};{master_degree.department}"
            master_degrees_dict['masters'][master_str] = master_degree.department

        print('master_degrees_dict: ', master_degrees_dict)

        secondary_value = secondary_map.get(result.secondary) if result else None
        higher_value = higher_map.get(result.higher) if result else None
        undergraduation_value = undergraduation_map.get(result.undergraduation) if result else None

        if result.secondary == 1:
            secondary_exam_type = 'SSC'

        elif result.secondary == 2:
            secondary_exam_type = 'O level'

        elif result.secondary == 3:
            secondary_exam_type = 'Dhakhil'

        else:
            higher_exam_type = 'N/A'

        if result.higher == 1:
            higher_exam_type = 'HSC'

        elif result.higher == 2:
            higher_exam_type = 'A level'

        elif result.higher == 3:
            higher_exam_type = 'Vocational'

        elif result.higher == 4:
            higher_exam_type = 'Diploma'

        else:
            higher_exam_type = 'N/A'

        # student result starts
        # Secondary education data
        education_data = []

        secondary_data = {
            'level': secondary_exam_type,
            'institute_name': 'N/A',
            'board': result.secondary_board,
            'result': result.secondary_result,
            'roll_no': result.secondary_roll_no if result.secondary_roll_no else 'N/A',
            'reg_no': result.secondary_reg_no if result.secondary_reg_no else 'N/A',
            'certificate_no': result.secondary_certificate_no if result.secondary_certificate_no else 'N/A',
            'passing_year': result.secondary_passing_year if result.secondary_passing_year else 'N/A',
            'certificate_copy': result.secondary_certificate_copy.url if result.secondary_certificate_copy else 'N/A',
            'created_at': result.created_at if result.created_at else 'N/A',
            'updated_at': result.updated_at if result.updated_at else 'N/A',
            'verification_status': result.secondary_verification_status,
            'result_id': result.id
        }
        education_data.append(secondary_data)

        # Higher education data
        higher_data = {
            'level': higher_exam_type,
            'institute_name': 'N/A',
            'board': result.higher_board,
            'result': result.higher_result,
            'roll_no': result.higher_roll_no if result.higher_roll_no else 'N/A',
            'reg_no': result.higher_reg_no if result.higher_reg_no else 'N/A',
            'certificate_no': result.higher_certificate_no if result.higher_certificate_no else 'N/A',
            'passing_year': result.higher_passing_year if result.higher_passing_year else 'N/A',
            'certificate_copy': result.higher_certificate_copy.url if result.higher_certificate_copy else 'N/A',
            'created_at': result.created_at if result.created_at else 'N/A',
            'updated_at': result.updated_at if result.updated_at else 'N/A',
            'verification_status': result.higher_verification_status,
            'result_id': result.id
        }
        education_data.append(higher_data)
        undergraduate_data = {
            'level': 'Undergraduate',
            'institute_name': result.university_name if result.university_name else 'N/A',
            'board': result.undergraduation_board,
            'result': result.undergraduation_result,
            'roll_no': 'N/A',
            'reg_no': 'N/A',
            'certificate_no': 'N/A',
            'passing_year': result.undergraduation_passing_year if result.undergraduation_passing_year else 'N/A',
            'certificate_copy': result.undergraduation_certificate_copy.url if result.undergraduation_certificate_copy else 'N/A',
            'created_at': result.created_at if result.created_at else 'N/A',
            'updated_at': result.updated_at if result.updated_at else 'N/A',
            'result_id': result.id
        }

        education_data.append(undergraduate_data)

        if masters_degrees.exists():
            for master in masters_degrees:
                masters_data = {
                    'level': f"Masters: {master.department}",
                    'institute_name': master.university if master.university else 'N/A',
                    'board': 'UGC',
                    'result': master.result if master.result else 'N/A',
                    'roll_no': 'N/A',
                    'reg_no': 'N/A',
                    'certificate_no': 'N/A',
                    'passing_year': master.passing_year if master.passing_year else 'N/A',
                    'certificate_copy': master.certificate_copy.url if master.certificate_copy else 'N/A',
                    'result_id': master.id,
                    'created_at': result.created_at if result.created_at else 'N/A',
                    'updated_at': result.updated_at if result.updated_at else 'N/A',
                }

                education_data.append(masters_data)

        # Other Certifications/Courses
        if other_certifications.exists():
            for course in other_certifications:
                course_data = {
                    'level': course.course_name.name,
                    'institute_name': course.institute if course.institute else 'N/A',
                    'board': 'UGC',
                    'result': course.result if course.result else 'N/A',
                    'roll_no': 'N/A',
                    'reg_no': 'N/A',
                    'certificate_no': 'N/A',
                    'passing_year': course.passing_year if course.passing_year else 'N/A',
                    'certificate_copy': course.certificate_copy.url if course.certificate_copy else 'N/A',
                    'result_id': course.id,
                    'created_at': course.created_at if course.created_at else 'N/A',
                    'updated_at': course.updated_at if course.updated_at else 'N/A'
                }

                education_data.append(course_data)


        student_data = {
            "id": student.id,
            "full_name": student.full_name,
            "student_user": student_user_id,
            "email": student.email,
            "phone": student.phone,
            "address": student.address,
            "gender": student.gender,
            'countries': countries_str,
            'student_image_url': student_image_url
        }

        # Prepare context for JSON response
        context = {
            'lead': lead,
            'student_level': {'student': student_data, 'level': lead},
            'student_details': student_details,
            'result': result,
            'education_data': education_data
        }

        # Return JSON response
        return JsonResponse(context, encoder=ModelJSONEncoder)
    


login_required(login_url='login_user')
@user_passes_test(is_consultant, login_url='login_user')
def consultant_feedback_list(request):
    consultant_id = get_logged_in_consultant(request.user).id
    feedback_list = HomeFeedback.objects.filter(consultant=consultant_id)
    print('type of consultant id in feedback: ', )
    print('feedback_list: ', feedback_list)

    for feedback in feedback_list:
        print('type of consultant id in feedback: ', type(feedback.consultant))

    # Fetch country names for each saved feedback
    for feedback in feedback_list:
        country_id = feedback.country
        feedback_country_ids_list = [int(country_id.strip()) for country_id in feedback.country.split(',')]
        print('feedback_country_ids_list: ', feedback_country_ids_list)
        try:
            feedback_countries_list = Countries.objects.filter(country_id__in=feedback_country_ids_list)
            country_names_list = [country.country_name for country in feedback_countries_list]
            country_names = ', '.join(map(str, country_names_list))
            feedback.country = country_names
        except Countries.DoesNotExist:
            feedback.country = "Unknown"

    # Get the count of new notifications
    new_notifications_count = feedback_list.filter(fdk_status=1).count()

    context = {
        'feedback_list': feedback_list,
        'consultant_id': consultant_id,
        'new_notifications_count': new_notifications_count
    }

    return render(request, 'Hodviews/consultant_feedback_list.html', context)


@login_required(login_url='login_user')
@user_passes_test(is_consultant, login_url='login_user')
def feedback_details_modal(request, feedback_id):
    feedback = get_object_or_404(HomeFeedback, id=feedback_id)
    return JsonResponse({'msg': feedback.fdk_msg, 'subject': feedback.subject})

@login_required(login_url='login_user')
@user_passes_test(is_consultant, login_url='login_user')
def delete_feedback(request, feedback_id):
    feedback = get_object_or_404(HomeFeedback, id=feedback_id)
    feedback.delete()
    return JsonResponse({'message': 'Feedback deleted successfully'})
    
    
    
    
    

def update_social_links(request):
    consultant = get_logged_in_consultant(request.user)
    consultant_id = consultant.id
    success_message = None
    error_message = None

    try:
        consultant_details = get_consultant_details_instance(consultant, create=True)
    except ConsultantDetails.DoesNotExist:
        consultant_details = None

    if request.method == 'POST':
        consultant_facebook = request.POST.get('consultant_facebook')
        consultant_website = request.POST.get('consultant_website')
        consultant_twitter = request.POST.get('consultant_twitter')
        consultant_googleplus = request.POST.get('consultant_googleplus')

        try:
            if consultant_details:
                consultant_details.consultant_facebook = consultant_facebook
                consultant_details.consultant_website = consultant_website
                consultant_details.consultant_twitter = consultant_twitter
                consultant_details.consultant_googleplus = consultant_googleplus
                consultant_details.save()
            else:
                consultant_details = get_consultant_details_instance(consultant, create=True)
                consultant_details.consultant_facebook = consultant_facebook
                consultant_details.consultant_website = consultant_website
                consultant_details.consultant_twitter = consultant_twitter
                consultant_details.consultant_googleplus = consultant_googleplus
                consultant_details.save()

            success_message = "Social links successfully updated."
        except Exception as e:
            error_message = f"Error updating social links: {str(e)}"

    return render(request, 'Hodviews/social_link.html', {
        'consultant_details': consultant_details,
        'success_message': success_message,
        'error_message': error_message
    })
    
    
def compare_balance_with_lead(request, lead, student_id):
    if request.method == 'GET':
        print('lead type: ', type(lead))
        print('student_id type: ', type(student_id))
        consultant_id = get_logged_in_consultant(request.user).id

        if lead and student_id:
            rate = Rates.objects.filter(rate_added_to=consultant_id).first()
            # balance = Balances.objects.filter(acc_pay_to=user.id).first()
            # Calculate total credit and debit for the consultant
            total_credit = Balances.objects.filter(acc_pay_to=consultant_id).aggregate(Sum('acc_credit'))['acc_credit__sum'] or 0.0
            total_debit = Balances.objects.filter(acc_paid_by=consultant_id).aggregate(Sum('acc_debit'))['acc_debit__sum'] or 0.0
            print('total_debit:', total_debit)
            
            # Calculate total balance
            total_balance = total_credit - total_debit
            print("total_balance:", total_balance)

            print('first lead: ', rate.first_rate)
            print('second lead: ', rate.second_rate)
            print('third lead: ', rate.third_rate)
            print('fourth lead: ', rate.four_rate)
            print('fifth lead: ', rate.five_rate)

            if lead == 1:
                lead_rate = round(rate.first_rate, 2)
            
            elif lead == 2:
                lead_rate = round(rate.second_rate, 2)

            elif lead == 3:
                lead_rate = round(rate.third_rate, 2)

            elif lead == 4:
                lead_rate = round(rate.four_rate, 2)

            elif lead == 5:
                lead_rate = round(rate.five_rate, 2)

            if total_balance < lead_rate:
                return JsonResponse({'insufficient_balance': f"You don't have enough balance to view the constact this student"})

            else:
                return JsonResponse({'success': True, 'message': f"To access the contact information of this student you will be charged BDT {lead_rate} from your available balance."})
                
                

@login_required(login_url='login_user')
@user_passes_test(is_consultant, login_url='login_user')
def total_balance_view(request):
    # Assuming consultant_id is related to the user
    consultant_id = get_logged_in_consultant(request.user).id

    # Calculate total credit and debit for the consultant
    total_credit = Balances.objects.filter(acc_pay_to=consultant_id).aggregate(Sum('acc_credit'))['acc_credit__sum'] or 0.0
    total_debit = Balances.objects.filter(acc_paid_by=consultant_id).aggregate(Sum('acc_debit'))['acc_debit__sum'] or 0.0
    
    # Calculate total balance
    total_balance = total_credit - total_debit

    # Return the total balance value as a plain HttpResponse
    return HttpResponse(total_balance)
    
    
def scholarship_list(request):
    uploaded_scholarships = ScholarShips.objects.all().order_by('-created_at')
    
    # Iterate through each uploaded scholarship to fetch the consultant's full name
    for scholarship in uploaded_scholarships:
        user = Users.objects.get(id=scholarship.consultant_id)
        scholarship.company_name = user.company_name
    
    # Pass the uploaded scholarships to the template context
    context = {'uploaded_scholarships': uploaded_scholarships}
    return render(request, 'Hodviews/consultant_wise_scholarship_list.html', context)
  






def edit_consultant_wise_scholarship_list(request, scholarship_id):
    instance = get_object_or_404(ScholarShips, id=scholarship_id)

    if request.method == 'POST':
        schp_description = request.POST.get('schp_description')
        apply_process = request.POST.get('apply_process')

        instance.schp_description = schp_description
        instance.apply_process = apply_process
        instance.updated_at = timezone.now()
        instance.save()

        messages.success(request, 'Consultant Wise Scholarship updated successfully.')
        return JsonResponse({'success': True})

    elif request.method == 'GET':
        data = {
            'schp_description': instance.schp_description,
            'apply_process': instance.apply_process,
        }
        return JsonResponse(data)

    else:
        # Return method not allowed for other request methods
        return JsonResponse({'success': False, 'message': 'Method Not Allowed'}, status=405)





    
    
    
    
    
