from django.urls import path
from django.urls import reverse_lazy
from .views import (
    HomeView,
    PostView,
    signup,
    log_in,
    log_out,
    profile,
    edit_profile,
    PostCreateView,
    PostUpdateView,
    PostDeleteView
)
from django.contrib.auth.views import (
    PasswordResetView,
    PasswordResetDoneView,
    PasswordResetConfirmView,
    PasswordResetCompleteView,
    PasswordChangeView,
    PasswordChangeDoneView
)

urlpatterns = [
    path('', HomeView.as_view(), name='home'),
    path('post/<pk>/<slug:slug>', PostView.as_view(), name='post'),
    path('signup/', signup, name='signup'),
    path('login/', log_in, name='login'),
    path('logout/', log_out, name='logout'),
    path('post/create/', PostCreateView.as_view(), name='post_create'),
    path('post/<int:pk>/', PostUpdateView.as_view(), name='post_update'),
    path('post/<int:pk>/delete/', PostDeleteView.as_view(), name='post_delete'),
    path('edit-profile/', edit_profile, name='edit_profile'),
    path('profile/<username>/', profile, name='profile'),
    path('password_reset/', PasswordResetView.as_view(
        template_name='password_reset.html',
        email_template_name='password_reset_email.html',
        subject_template_name='password_reset_subject.txt',
        success_url='/password_reset/done/'),
         name='password_reset'
         ),
    path('password_reset/done/', PasswordResetDoneView.as_view(
        template_name='users/password_reset_done.html'),
         name='password_reset_done'
         ),
    path('reset/<uidb64>/<token>/', PasswordResetConfirmView.as_view(
        template_name='users/password_reset_confirm.html',
        success_url='/users/reset/done/'),
         name='password_reset_confirm'
         ),
    path('reset/done/', PasswordResetCompleteView.as_view(
        template_name='password_reset_complete.html'),
         name='password_reset_complete'
         ),
    path('password_change/', PasswordChangeView.as_view(
        template_name='password_change.html',
        success_url=reverse_lazy('core:password_change_done')),
        name='password_change'),
    path('password_change/done/', PasswordChangeDoneView.as_view(
        template_name='password_change_done.html'),
        name='password_change_done'),

]
