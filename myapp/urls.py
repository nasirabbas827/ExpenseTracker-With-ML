from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth.decorators import login_required

urlpatterns = [
    # Your other URL patterns
    path('register/', views.user_register, name='user_register'),
    path('', views.user_login, name='user_login'),
    path('dashboard/', login_required(views.dashboard), name='dashboard'),  # Add this line
    path('update_profile/', login_required(views.update_profile), name='update_profile'),
    path('change_password/', login_required(views.change_password), name='change_password'),
    path('logout/', views.logout_view, name='logout'),
    path('categories/add/', views.add_category, name='add_category'),
    path('categories/', views.view_categories, name='view_categories'),
    path('categories/edit/<int:pk>/', views.edit_category, name='edit_category'),
    path('categories/delete/<int:pk>/', views.delete_category, name='delete_category'),
    path('income/add/', views.add_income, name='add_income'),
    path('income/', views.view_income, name='view_income'),
    path('income/edit/<int:pk>/', views.edit_income, name='edit_income'),
    path('income/delete/<int:pk>/', views.delete_income, name='delete_income'),
    path('expense/add/', views.add_expense, name='add_expense'),
    path('expense/', views.view_expense, name='view_expense'),
    path('expense/edit/<int:pk>/', views.edit_expense, name='edit_expense'),
    path('expense/delete/<int:pk>/', views.delete_expense, name='delete_expense'),
    path('income/export/csv/', views.export_income_csv, name='export_income_csv'),
    path('expenses/export/csv/', views.export_expense_csv, name='export_expense_csv'),

]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
