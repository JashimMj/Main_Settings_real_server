from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('umpapi/login/', views.loginV,name='login'),
    path('', views.index,name='index'),
    path('maindashboard/', views.maindashboardV,name='maindashboard'),
    path('admindashboard/', views.admindashboardV,name='admindashboard'),
    # path('company/and/branch/', views.companyandbranchV,name='companyandbranch'),
    # path('company/and/branch/save', views.CompanySaveV,name='companyandbranchsave'),
    path('umpapi/', views.UMP_APIV,name='umpapi'),
    path('umpapi/deposited/', views.UMP_deposit,name='deposit'),
    path('umpapi/deposited/send/', views.UMP_depositedV,name='deposit_send'),
    path('umpapi/ss/', views.UMP_APIsV,name='umpapiss'),
    path('umpapi/sended/', views.UMP_APIsendeV,name='umpapissended'),
    path('umpapi/previous/report', views.previouslysende,name='umpsedp'),
    path('umpapi/previous/report/PDF/', views.previouslysendePDFV,name='umpsedPDF'),
    path('umpapi/Logout/', views.logoutV,name='logout'),
    path('otp/', views.otpV,name='otps'),
    path('login/otp/', views.finalloginV,name='loginotp'),
    path('MR/search/', views.MrserarchV,name='mrnoserach'),
    path('all/report/', views.AllsendedV,name='allreport'),
    path('chat/send/', views.chatV,name='chat'),
    path('chat/search/', views.searchV,name='search'),
    path('admins/comment/<int:id>/', views.AcommentV,name='Acomment'),
    path('admins/update/<int:id>/', views.AcommenteditV,name='updatea'),
    path('MRUMP/', views.UMP_APIMRV,name='MRUMP'),
    path('MRUMP/deposit/', views.UMP_APdepositV,name='MRUMPdepos'),












]+ static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
