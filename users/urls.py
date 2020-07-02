from django.urls import path
from . import views
from django.views.generic import DetailView
from .models import CustomUser
from .forms import UserUpToAdminForm


class ProfileView(DetailView):
    model = CustomUser
    context_object_name = 'smbusr'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['user_up_to_admin_form'] = UserUpToAdminForm
        return context


urlpatterns = [
    path('reg/', views.registration),
    path('auth/', views.authorization),
    path('restore/', views.restore),
    path('logout/', views.log_out),
    path('user/<int:pk>/', ProfileView.as_view(template_name='profile.html')),
    path('makeadmin/', views.make_admin),
    path('user/change/', views.user_change),
    path('user/changepassword/', views.pass_change),
]
