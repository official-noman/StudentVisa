# visa/context_processors.py

from .models import Users,ConsultantDetails
from visa.models import StudentDetails,MastersDegree, OtherCertification, Results
from django.db.models import Q
from django.core.exceptions import ObjectDoesNotExist
def user_data(request):
    # Your logic to retrieve user data
    user_data = None
    if request.user.is_authenticated:
        user_data = Users.objects.filter(consultant_user=request.user).first()
    return {'user_data': user_data}



def consultant_details(request):
    consultant_details = None
    if request.user.is_authenticated:
        consultant_user = Users.objects.filter(consultant_user=request.user).first()
        if consultant_user:
            consultant_details = ConsultantDetails.objects.filter(consultant_id=consultant_user.id).first()
            if consultant_details is None and consultant_user.consultant_user_id:
                consultant_details = ConsultantDetails.objects.filter(
                    consultant_id=consultant_user.consultant_user_id
                ).first()
                if consultant_details:
                    consultant_details.consultant_id = consultant_user.id
                    consultant_details.save(update_fields=["consultant_id"])
    return {'consultant_details': consultant_details}



def consultant_user_details(request):
    consultant_user_details = None
    if request.user.is_authenticated:
        consultant_user_details = Users.objects.filter(consultant_user=request.user).first()
    return {'consultant_user_details': consultant_user_details, 'request': request}
    
    
def fav_consultant_ids(request):
    # Check if the user is authenticated
    if request.user.is_authenticated:
        try:
            # Retrieve student details if available
            student_details = StudentDetails.objects.get(dets_regs_id=request.user.id)
            # Split the comma-separated list of favorite consultant IDs
            if student_details.dets_favconsultantlist:
                fav_consultant_ids = [int(id) for id in student_details.dets_favconsultantlist.split(',')]
            else:
                fav_consultant_ids = []
        except ObjectDoesNotExist:
            # Handle the case when StudentDetails for the user does not exist
            fav_consultant_ids = []
    else:
        # User is not authenticated, set an empty list
        fav_consultant_ids = []

    # Return the dictionary with the favorite consultant IDs
    return {'fav_consultant_ids': fav_consultant_ids}
    
    

def verification_statuses(request):
    student_id = request.session.get('student_id')
    verification_status = 'not_verified'  # Default status

    if student_id:
        # Check if any uploaded certificate copy for the student is verified
        if Results.objects.filter(
            student_id=student_id
        ).filter(
            (
                Q(higher_certificate_copy__isnull=False, higher_verification_status='verified') |
                Q(secondary_certificate_copy__isnull=False, secondary_verification_status='verified') |
                Q(diploma_certificate_copy__isnull=False, diploma_verification_status='verified') |
                Q(undergraduation_certificate_copy__isnull=False, undergraduation_verification_status='verified') |
                Q(phd_certificate_copy__isnull=False, phd_verification_status='verified')
            )
        ).exists():
            verification_status = 'verified'

    return {'verification_status': verification_status}
