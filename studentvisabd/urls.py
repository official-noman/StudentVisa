"""
URL configuration for studentvisabd project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from visa import views,Hodviews,rootviews
from django.conf import settings
from django.conf.urls.static import static
import django.views.static
from django.urls import re_path
from django.views.static import serve

urlpatterns = [

    path('', views.home, name='home'),
    path('contact/', views.contact, name='contact'),
 path('meta/', views.meta, name='meta'),
    path('consultant_list/', views.consultant_list, name='consultant_list'),
    path('single_consultant_details/<int:consultant_id>/', views.singel_consultant_details, name='singel_consultant_details'),
    path('single_consultant_page/<int:consultant_id>/', views.singel_consultant_page, name='singel_consultant_page'),
    path('single_consultant_gallery/<int:consultant_id>/', views.singel_consultant_gallery, name='singel_consultant_gallery'),
    path('single_consultant_requirement/<int:consultant_id>/', views.single_consultant_requirement, name='single_consultant_requirement'),
    path('single_consultant_country/<int:consultant_id>/', views.singel_consultant_country, name='singel_consultant_country'),
    path('single_consultant_country_details/<int:consultant_id>/<int:country_id>/', views.singel_consultant_country_details, name='singel_consultant_country_details'),
    path('single_consultant_review/<int:consultant_id>/', views.singel_consultant_review, name='singel_consultant_review'),
    path('single_consultant_all_reviews/<int:consultant_id>/', views.single_consultant_all_reviews, name='single_consultant_all_reviews'),
    path('single_consultant_profile/<int:consultant_id>/', views.singel_consultant_profile, name='singel_consultant_profile'),
    path('single_consultant_contact/<int:consultant_id>/', views.singel_consultant_contact, name='single_consultant_contact'),
    path('feedback/<int:consultant_id>/', views.feedback, name='feedback'),
    path('save_feedback/', views.save_feedback, name='save_feedback'),
    path('save_review/', views.save_review, name='save_review'),
    path('country_details/<int:country_id>/', views.country_details, name='country_details'),
     path('colors/<int:consultant_id>/', views.colors, name='colors'),


    path('consaltant_wise_scholarship/', views.consaltant_wise_scholarship, name='consaltant_wise_scholarship'),
    path('scholarship_singel_page/<int:scholarship_id>/', views.consaltant_wise_scholarship_singel_page, name='scholarship_singel_page'),
    path('process_explanation/',views.process_explanation, name='process_explanation'),
    path('country_wise_scholarship/', views.country_wise_scholarship, name='country_wise_scholarship'),
    path('offer_letter/', views.offer_letter, name='offer_letter'),
    path('by_country/', views.by_country, name='by_country'),
    path('signup_user/', views.signup_user, name='signup_user'),
    path('redirect_to_otp/', views.redirect_to_otp, name='redirect_to_otp'),
    path('signup_student/', views.signup_student, name='signup_student'),
    path('login_user/', views.login_user, name='login_user'),
    path('login_student/', views.login_student, name='login_student'),
    path('logout/', views.logout_user, name='logout'),
    path('get_thana/', views.get_thana, name='get_thana'),
    path('otp_verification_signup/', views.otp_verification_signup, name='otp_verification_signup'),
    path('otp_verification_signup_student/', views.otp_verification_signup_student, name='otp_verification_signup_student'),
    path('admin/', views.login_admin, name='admin'),
    path('save_user_signup/', views.save_user_signup, name='save_user_signup'),
    path('save_student_signup/', views.save_student_signup, name='save_student_signup'),
    path('country_wise_scholarship_single/<int:scw_id>/', views.country_wise_scholarship_single, name='country_wise_scholarship_single'),
    
    path('addresses/', views.address_view, name='addresses'),
    path('feedback_home/', views.feedback_view, name='feedback-home'),
    path('maps/',views.map_view, name='maps'),
    path('by_country_autosearch/', views.by_country_autosearch, name='by_country_autosearch'),
    path('forgot_password_phone_or_email/', views.forgot_password_phone_or_email, name='forgot_password_phone_or_email'),
    path('forgot_password_otp_verification/', views.forgot_password_otp_verification, name='forgot_password_otp_verification'),
    path('change_forgotten_password/', views.change_forgotten_password, name='change_forgotten_password'),
    path('forgot_password_phone_or_email_student/', views.forgot_password_phone_or_email_student, name='forgot_password_phone_or_email_student'),
    path('forgot_password_otp_verification_student/', views.forgot_password_otp_verification_student, name='forgot_password_otp_verification_student'),
    path('change_forgotten_password_student/', views.change_forgotten_password_student, name='change_forgotten_password_student'),
    path('change_number/', views.change_number, name='change_number'),
    path('consultant_list_autosearch/', views.consultant_list_autosearch, name='consultant_list_autosearch'),
            path('check_phone_exist_user/', views.check_phone_exist_user, name='check_phone_exist_user'),
        path('check_email_exist_user/', views.check_email_exist_user, name='check_email_exist_user'),
        path('check_phone_exist_student/', views.check_phone_exist_student, name='check_phone_exist_student'),
        path('check_email_exist_student/', views.check_email_exist_student, name='check_email_exist_student'),


    # Student Info
    path('student_home/', views.student_home, name='student_home'),
    path('student_result_information/', views.student_result_information, name="student_result_information"),
    path('student_search_consultant/', views.student_search_consultant, name='student_search_consultant'),
    path('add_to_favorite/<int:consultant_id>/', views.add_to_favorite, name='add_to_favorite'),
    path('student_favourite_list/', views.student_favourite_list, name='student_favourite_list'),
    path('student_profile/', views.student_profile, name="student_profile"),
    path('edit_student_profile/', views.edit_student_profile, name="edit_student_profile"),
    path('delete_favourite_consultant/<int:consultant_id>/', views.delete_favourite_consultant, name='delete_favourite_consultant'),
    path('destroy_session/', views.destroy_session, name="destroy_session"),
    path('get_exam_type/', views.get_exam_type, name="get_exam_type"),
    path('change_student_password/', views.change_student_password, name="change_student_password"),
    path('save_secondary_result_information/', views.save_secondary_result_information, name="save_secondary_result_information"),
    path('save_higher_result_information/', views.save_higher_result_information, name="save_higher_result_information"),
    path('save_undergraduation_result_information/', views.save_undergraduation_result_information, name="save_undergraduation_result_information"),
    path('save_masters_result_information/', views.save_masters_result_information, name="save_masters_result_information"),
    path('save_phd_result_information/', views.save_phd_result_information, name="save_phd_result_information"),
    path('save_other_certification_result_information/', views.save_other_certification_result_information, name="save_other_certification_result_information"),


    #Consultant 
    path('consultant_home/', Hodviews.consultant_home, name="consultant_home"),
    path('consultant_gallery/', Hodviews.consultant_gallery, name="consultant_gallery"),
    path('consultant_profile/', Hodviews.consultant_profile, name="consultant_profile"),
    path('save_consultant_profile/<int:user_id>/', Hodviews.save_consultant_profile, name="save_consultant_profile"),
    path('consultant_logo/', Hodviews.consultant_logo, name="consultant_logo"),
    path('save_logo/', Hodviews.save_logo, name="save_logo"),
    

    path('consultant_requirement/', Hodviews.consultant_requirement, name="consultant_requirement"),
    path('consultant_country/', Hodviews.consultant_country, name="consultant_country"),
    path('delete_country/', Hodviews.delete_country, name="delete_country"),
    path('monthly_balance_chart/', Hodviews.monthly_balance_chart, name='monthly_balance_chart'),
    path('consultant_ratings_json/', Hodviews.consultant_ratings_json ,name="consultant_ratings_json"),
    # path('consultant_scholarship_hod/', Hodviews.consultant_scholarship, name="consultant_ scholarship_hod"),
    path('consultant_feedback_list/', Hodviews.consultant_feedback_list, name='consultant_feedback_list'),
    path('consultant_wise/', Hodviews.consultant_scholarship, name="consultant_wise"),
    path('consultant_map/', Hodviews.consultant_map, name="consultant_map"),
    path('linkpage/', Hodviews.linkpage, name="linkpage"),
    path('consultant_color/', Hodviews.consultant_color, name="consultant_color"),
    path('consultant_intro/', Hodviews.consultant_intro, name="consultant_intro"),
    path('student_list/', Hodviews.student_list, name="student_list"),
    path('update-my-lead/', Hodviews.update_my_lead, name='update_my_lead'),
    path('view_students_by_consultant/<int:lead>/<int:student_id>/', Hodviews.view_students_by_consultant, name='view_students_by_consultant'),
    path('update-balance/<int:lead>/<int:student_id>/', Hodviews.update_balance, name='update_balance'),
    path('country-wise-scholarship-list/', rootviews.country_wise_scholarship_list, name='country_wise_scholarship_list'),
    path('edit-scholarship/<int:scw_id>/', rootviews.edit_scholarship, name='edit_scholarship'),
    path('delete-scholarship/<int:scw_id>/', rootviews.delete_scholarship, name='delete_scholarship'),
    path('feedback_details_modal/<int:feedback_id>/', Hodviews.feedback_details_modal, name='feedback_details_modal'),
    path('delete_feedback/<int:feedback_id>/', Hodviews.delete_feedback, name='delete_feedback'),
    path('compare_balance_with_lead/<int:lead>/<int:student_id>/', Hodviews.compare_balance_with_lead, name='compare_balance_with_lead'),
    path('new_students_view/', Hodviews.new_students_view, name='new_students_view'),
     path('delete_gallery/<int:image_id>/', Hodviews.delete_gallery, name='delete_gallery'),
     path('total_balance/', Hodviews.total_balance_view, name='total_balance_view'),
         path('scholarship_list/', Hodviews.scholarship_list, name='scholarship_list'),
    
  path('edit_consultant_wise_scholarship_list/<int:scholarship_id>/', Hodviews.edit_consultant_wise_scholarship_list, name='edit_consultant_wise_scholarship'),
          path('update_social_links/', Hodviews.update_social_links, name='update_social_links'),


    



    #Root
    path('root_home/', rootviews.root_home, name="root_home"),
    path('root_customize/', rootviews.root_customize, name='root_customize'),
    path('root_countries/', rootviews.root_countries, name='root_countries'),
    path('offer_letters/', rootviews.offer_letters, name='offer_letters'),
    path('edit_country/<int:country_id>/', rootviews.edit_country, name='edit_country'),
    path('delete_country/<int:country_id>/', rootviews.delete_country, name='delete_country'),
   path('consultant_wise_root/', rootviews.consultant_wise_scholarship, name='consultant_wise_root'),
    path('country_wise/', rootviews.country_wise_scholarship, name='country_wise'),
    path('university_wise/', rootviews.university_wise_scholarship, name='university_wise'),
    path('root_users_list/', rootviews.root_users_list, name='root_users_list'),
    path('create_root/', rootviews.create_root, name='create_root'),
     path('grant_permission/<int:user_id>/',rootviews.grant_permission, name='grant_permission'),

     path('grant_permission_consultant/<int:user_id>/',rootviews.grant_permission_consultant, name='grant_permission_consultant'),

    path('root_consultant_list/', rootviews.root_consultant_list, name='root_consultant_list'),
    path('reject_consultant/<int:user_id>/', rootviews.reject_consultant, name='reject_consultant'),
     path('activeconsultant/', rootviews.activeconsultant, name='activeconsultant'),
     path('activeconsultant/details/<int:user_id>/', rootviews.active_consultant_details, name='active_consultant_details'),
    path('activeconsultant/suspend/<int:user_id>/', rootviews.suspend_account, name='suspend_account'),
    path('suspend_list/', rootviews.suspend_list, name='suspend_list'),
    path('suspendedconsultant/details/<int:user_id>/', rootviews.suspended_consultant_details, name='suspended_consultant_details'),
    path('suspendedconsultant/activate/<int:user_id>/', rootviews.activate_account, name='activate_account'),
        path('free_account/<int:user_id>/', rootviews.free_account, name='free_account'),

        # For listing free consultants
    path('free_list/', rootviews.free_list, name='free_list'),

        # For retrieving details of a free consultant
    path('free_consultant_details/<int:user_id>/', rootviews.free_consultant_details, name='free_consultant_details'),
    path('activate_basic_account/<int:user_id>/', rootviews.activate_basic_account, name='activate_basic_account'),
      path('basic_list/', rootviews.basic_list, name='basic_list'),

    path('basic_user_details/<int:user_id>/', rootviews.basic_user_details, name='basic_user_details'),
    
    path('activate_premium_account/<int:user_id>/', rootviews.activate_premium_account, name='activate_premium_account'),
    path('premium_list/', rootviews.premium_list, name='premium_list'),
    path('premium_user_details/<int:user_id>/', rootviews.preimum_user_details, name='preimum_user_details'),
    #  path('root_student_list/', rootviews.inactive_students_list, name='root_student_list'),
    path('suspend_student_account/<int:student_id>/', rootviews.make_suspend, name='suspend_student_account'),
    path('suspended_students_list/', rootviews.suspended_students_list, name='suspended_students_list'),


     path('inactive_students_details/<int:student_id>/', rootviews.students_details, name='inactive_students_details'),
     path('activate_student_account/<int:student_id>/', rootviews.activate_student_account, name='activate_student_account'),
     path('active_student_list/', rootviews.active_student_list, name='active_student_list'),
      path('active_student_details/<int:student_id>/', rootviews.active_student_details, name='active_student_details'),
      path('verify_student_account/<int:student_id>/', rootviews.verify_student_account, name='verify_student_account'),

    path('verify_student_list/', rootviews.verify_student_list, name='verify_student_list'),
      path('verify_student_details/<int:student_id>/', rootviews.verify_student_details, name='verify_student_details'),
    path('consultant_credit_balance/', rootviews.consultant_credit_balance, name='consultant_credit_balance'),
    path('consultant_rates/', rootviews.consultant_rates, name='consultant_rates'),
    path('add_or_update_rates/<int:consultant_id>/', rootviews.add_or_update_rates, name='add_or_update_rates'),
       path('get_existing_rates/<int:consultant_id>/', rootviews.get_existing_rates, name='get_existing_rates'),
       path('get_existing_permissions/<int:user_id>/', rootviews.get_existing_permissions, name='get_existing_permissions'),

     path('add_address/', rootviews.add_address, name='add_address'),
      path('monthly_balance_chart_root/', rootviews.monthly_balance_chart, name='monthly_balance_chart_root'),
       path('type_of_balance/', rootviews.type_of_balance, name='type_of_balance'),
        path('root_consultant_list_json/', rootviews.root_consultant_list_json, name='root_consultant_list_json'),
        path('count_consultant_perform/', rootviews.count_consultant_perform, name='count_consultant_perform'),
        path('count_students_monthly_entry/', rootviews.count_students_monthly_entry, name='count_students_monthly_entry'),
        path('count_students_yearly_entry/', rootviews.count_students_yearly_entry, name='count_students_yearly_entry'),
        path('count_students_weekly_entry/', rootviews.count_students_weekly_entry, name='count_students_weekly_entry'),
        path('message_list/', rootviews.message_list, name='message_list'),
        path('create_reply/<int:message_id>/', rootviews.create_reply, name='create_reply'),
        path('get_chat_history/<int:message_id>/', rootviews.get_chat_history, name='get_chat_history'),
        path('root_profile/', rootviews.root_profile, name="root_profile"),
        path('save_root_profile/<int:user_id>/', rootviews.save_root_profile, name="save_root_profile"),
        path('explenation/', rootviews.process_explenation_root, name='explenation'),
        path('update_client/<int:client_id>/', rootviews.update_client, name='update_client'),
        path('delete_client/<int:client_id>/', rootviews.delete_client, name='delete_client'),
        path('client_list/', rootviews.client_list, name='client_list'),
        path('add_client/', rootviews.add_client, name='add_client'),
        path('export_dashboard_data/', rootviews.export_dashboard_data, name='export_dashboard_data'),
        path('save-benefit/', rootviews.save_benefit_for_consultant, name='save_benefit'),
                  path('balance/', rootviews.balance_list, name='balance-list'),
                     path('check_phone_exist/', rootviews.check_phone_exist, name='check_phone_exist'),
                  path('check_email_exist/', rootviews.check_email_exist, name='check_email_exist'),
                  
        path('get_consultant_balance/', rootviews.get_consultant_balance, name='get_consultant_balance'),
        path('get_last_transactions/', rootviews.get_last_transactions, name='get_last_transactions'),
        path('get_all_consultants/', rootviews.get_all_consultants, name='get_all_consultants'),
        path('consultant-wise-scholarship-list/', rootviews.consultant_wise_scholarship_list, name='consultant_wise_scholarship_list'),
     path('edit_consultant_wise_scholarship/<int:scow_id>/', rootviews.edit_consultant_wise_scholarship, name='edit_consultant_wise_scholarship'),
    path('delete_consultant_wise_scholarship/<int:scow_id>/', rootviews.delete_consultant_wise_scholarship, name='delete_consultant_wise_scholarship'),
             path('consutlant_upload/', rootviews.consutlant_upload, name='consutlant_upload'),
        path('view-scholarship/<int:scholarship_id>/', rootviews.view_scholarship, name='view_scholarship'),
        path('delete_scholarship_uploaded/<int:scholarship_id>/', rootviews.delete_scholarship_uploaded, name='delete_scholarship_uploaded'),
         path('approve-scholarship/', rootviews.approve_scholarship, name='approve_scholarship'),
         path('course_list/', rootviews.course_list, name='course_list'),
    path('add_course/', rootviews.add_course, name='add_course'),
    path('edit_course/<int:course_id>/', rootviews.edit_course, name='edit_course'),
    path('delete_course/<int:course_id>/', rootviews.delete_course, name='delete_course'),
    path('update_verification_status/', rootviews.update_verification_status, name='update_verification_status'),






    re_path(r'^media/(?P<path>.*)$', serve, {'document_root': settings.MEDIA_ROOT}),





 


  
    


]
handler404 = 'visa.views.custom_404_view'

# Add media and static URLs in development mode
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

# elif getattr(settings, 'FORCE_SERVE_STATIC', False):
#     settings.DEBUG = True
#     urlpatterns += static(
#         settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
#     urlpatterns += static(
#         settings.STATIC_URL, document_root=settings.STATIC_ROOT)
#     settings.DEBUG = False