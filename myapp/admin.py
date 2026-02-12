from django.contrib import admin
from .models import Profile, Category, Income, Expense


# ==========================================
# PROFILE ADMIN
# ==========================================
@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = (
        'user',
        'full_name',
        'email',
        'gender',
        'age',
    )
    search_fields = ('user__username', 'full_name', 'email')
    list_filter = ('gender',)
    ordering = ('user',)


# ==========================================
# CATEGORY ADMIN
# ==========================================
@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('category_id', 'name')
    search_fields = ('name',)
    ordering = ('name',)


# ==========================================
# INCOME ADMIN
# ==========================================
@admin.register(Income)
class IncomeAdmin(admin.ModelAdmin):
    list_display = (
        'income_id',
        'user',
        'source',
        'amount',
        'date',
    )
    search_fields = ('user__username', 'source')
    list_filter = ('date',)
    ordering = ('-date',)
    date_hierarchy = 'date'


# ==========================================
# EXPENSE ADMIN
# ==========================================
@admin.register(Expense)
class ExpenseAdmin(admin.ModelAdmin):
    list_display = (
        'expense_id',
        'user',
        'category',
        'amount',
        'date',
    )
    search_fields = ('user__username', 'category__name')
    list_filter = ('category', 'date')
    ordering = ('-date',)
    date_hierarchy = 'date'


 