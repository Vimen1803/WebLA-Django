from django.urls import re_path
from clubs import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    # Página principal
    re_path(r'^$|^home/?$', views.main_page, name='main_page'),

    # Clubs: lista y detalle
    re_path(r'^clubs/?$', views.clubs_view, name='clubs_list'),
    re_path(r'^clubs/(?P<club_tag>[^/]+)/?$', views.club_detail_view, name='club_detail'),

    # Tops: home y lista con límite
    re_path(r'^tops/?$', views.tops_home, name='tops_home'),
    re_path(r'^tops/(?P<limit>[^/]+)/?$', views.top_players_list, name='top_players_list'),

    # Miembros
    re_path(r'^member/(?P<player_tag>[^/]+)/?$', views.member_detail_view, name='member_detail'),

    # Login y logout
    re_path(r'^login/?$', auth_views.LoginView.as_view(
        template_name='clubs/login.html',
        redirect_authenticated_user=False
    ), name='login'),
    re_path(r'^logout/?$', views.CustomLogoutView.as_view(), name='logout'),

    # Admin
    re_path(r'^admin/?$', views.admin_view, name='admin_view'),
]
