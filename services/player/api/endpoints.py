from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', views.GamerInfo.as_view(), name='gamerInfoView'),
    path('avatar/', views.GamerAvatarUpload.as_view(), name='gamerAvatarUploadView'),
    path('friendship/', views.GamerFriendship.as_view(), name='gamerFriendshipView'),
    path('matches/', views.MatchesHistory.as_view(), name='matchesHistoryView'),
]

urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
