from decimal import Decimal
import csv

from django.contrib import messages
from django.contrib.auth import login, authenticate, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm
from django.db.models import Sum
from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error
from datetime import datetime
from dateutil.relativedelta import relativedelta
import plotly.express as px
import plotly.graph_objects as go


from .forms import (
    ProfileForm, CategoryForm, RegistrationForm, LoginForm,
    IncomeForm, ExpenseForm
)
from .models import Profile, Category, Income, Expense


# ───────────────────────────────────────────────
# Authentication & Profile Views
# ───────────────────────────────────────────────

def user_register(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "Registration successful! Welcome to Expense Tracker.")
            return redirect('dashboard')
    else:
        form = RegistrationForm()
    return render(request, 'register.html', {'form': form})


def user_login(request):
    if request.method == 'POST':
        form = LoginForm(request, request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, "You have successfully logged in.")
            return redirect('dashboard')
        else:
            messages.error(request, "Invalid username or password.")
    else:
        form = LoginForm(request=request)
    return render(request, 'login.html', {'form': form})


def logout_view(request):
    logout(request)
    messages.info(request, "You have been logged out.")
    return redirect('user_login')




@login_required
def dashboard(request):
    user = request.user

    # ─── Core summary numbers ────────────────────────────────────────
    total_income = Income.objects.filter(user=user).aggregate(
        total=Sum('amount')
    )['total'] or Decimal('0')

    total_expenses = Expense.objects.filter(user=user).aggregate(
        total=Sum('amount')
    )['total'] or Decimal('0')

    balance = total_income - total_expenses

    # ─── Category distribution (optimized - avoids N+1 queries) ──────
    cat_totals = (
        Expense.objects.filter(user=user)
        .values('category__name')
        .annotate(total=Sum('amount'))
        .order_by('category__name')
    )

    cat_data = [
        {'category': item['category__name'], 'amount': float(item['total'])}
        for item in cat_totals if item['total'] > 0
    ]
    cat_df = pd.DataFrame(cat_data)

    # ─── Monthly expense data ────────────────────────────────────────
    monthly_exp = (
        Expense.objects.filter(user=user)
        .extra(select={'month': "strftime('%%Y-%%m', date)"})
        .values('month')
        .annotate(total=Sum('amount'))
        .order_by('month')
    )

    df_exp = pd.DataFrame(list(monthly_exp))

    # ─── Monthly income data (for income prediction) ─────────────────
    monthly_inc = (
        Income.objects.filter(user=user)
        .extra(select={'month': "strftime('%%Y-%%m', date)"})
        .values('month')
        .annotate(total=Sum('amount'))
        .order_by('month')
    )

    df_inc = pd.DataFrame(list(monthly_inc))

    # ─── Linear Regression Prediction ────────────────────────────────
    exp_prediction = None
    exp_mae = None
    inc_prediction = None
    inc_mae = None
    next_month_name = "—"
    exp_message = "Not enough expense data (need ≥ 4 months)"
    inc_message = "Not enough income data (need ≥ 4 months)"

    def predict_trend(df, column='total'):
        if len(df) < 4:
            return None, None

        df[column] = df[column].astype(float)
        df['month_num'] = np.arange(len(df))

        X = df[['month_num']].to_numpy()  # ← removes feature name warning
        y = df[column].to_numpy()

        model = LinearRegression()
        model.fit(X, y)

        next_num = df['month_num'].max() + 1
        pred_value = model.predict([[next_num]])[0]
        pred = max(0, round(float(pred_value), 2))

        y_pred = model.predict(X)
        error = mean_absolute_error(y, y_pred)

        return pred, error

    if not df_exp.empty:
        last_month_str = df_exp['month'].iloc[-1]
        year, month = map(int, last_month_str.split('-'))
        next_date = datetime(year, month, 1) + relativedelta(months=1)
        next_month_name = next_date.strftime("%B %Y")

        # Expense prediction
        exp_prediction, exp_mae = predict_trend(df_exp)
        if exp_prediction is not None:
            exp_message = (
                f"<strong>Expenses:</strong> Rs {exp_prediction:,.2f} "
                f"<small>(error ≈ Rs {exp_mae:,.0f})</small>"
            )

        # Income prediction (optional)
        inc_prediction, inc_mae = predict_trend(df_inc)
        if inc_prediction is not None:
            inc_message = (
                f"<strong>Income:</strong> Rs {inc_prediction:,.2f} "
                f"<small>(error ≈ Rs {inc_mae:,.0f})</small>"
            )

    # ─── Plotly Charts ───────────────────────────────────────────────

    # Category Pie Chart
    pie_html = None
    if not cat_df.empty:
        fig_pie = px.pie(
            cat_df,
            values='amount',
            names='category',
            title='Expenses by Category',
            hole=0.35,
            color_discrete_sequence=px.colors.qualitative.Set2
        )
        fig_pie.update_traces(textposition='inside', textinfo='percent+label')
        fig_pie.update_layout(showlegend=True, margin=dict(t=60, b=20, l=20, r=20), height=420)
        pie_html = fig_pie.to_html(full_html=False, config={'responsive': True})

    # Monthly Expense Trend Chart
    trend_html = None
    if not df_exp.empty:
        df_exp['month'] = df_exp['month'].astype(str)
        fig_trend = go.Figure()

        fig_trend.add_trace(go.Bar(
            x=df_exp['month'],
            y=df_exp['total'],
            name='Expenses',
            marker_color='rgba(239, 83, 80, 0.65)'
        ))

        fig_trend.add_trace(go.Scatter(
            x=df_exp['month'],
            y=df_exp['total'],
            mode='lines+markers',
            name='Trend',
            line=dict(color='#2196F3', width=2.5),
            marker=dict(size=8)
        ))

        fig_trend.update_layout(
            title='Monthly Expense Trend',
            xaxis_title='Month',
            yaxis_title='Amount (Rs)',
            hovermode='x unified',
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
            margin=dict(t=70, b=50, l=50, r=30),
            height=420,
            template='plotly_white'
        )
        trend_html = fig_trend.to_html(full_html=False, config={'responsive': True})

    # ─── Context ─────────────────────────────────────────────────────
    context = {
        'username': user.username,
        'total_income': float(total_income),
        'total_expenses': float(total_expenses),
        'balance': float(balance),
        'pie_chart': pie_html,
        'trend_chart': trend_html,
        'exp_message': exp_message,
        'inc_message': inc_message,
        'exp_prediction': exp_prediction,
        'exp_mae': exp_mae,
        'next_month_name': next_month_name,
        'has_data': bool(cat_df.shape[0] or df_exp.shape[0]),
    }

    return render(request, 'dashboard.html', context)

@login_required
def update_profile(request):
    # Get or create the profile (safe even if it doesn't exist yet)
    profile, created = Profile.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, "Your profile has been updated successfully.")
            return redirect('update_profile')
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = ProfileForm(instance=profile)

    context = {
        'form': form,
        'profile': profile,           
    }

    return render(request, 'update_profile.html', context)


@login_required
def change_password(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            messages.success(request, 'Your password was successfully updated!')
            return redirect('dashboard')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = PasswordChangeForm(request.user)

    return render(request, 'change_password.html', {'form': form})


# ───────────────────────────────────────────────
# Category Management
# ───────────────────────────────────────────────

@login_required
def add_category(request):
    if request.method == 'POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Category added successfully.')
            return redirect('view_categories')
    else:
        form = CategoryForm()

    return render(request, 'add_category.html', {'form': form})


@login_required
def view_categories(request):
    categories = Category.objects.all().order_by('name')
    return render(request, 'view_categories.html', {'categories': categories})


@login_required
def edit_category(request, pk):
    category = get_object_or_404(Category, pk=pk)

    if request.method == 'POST':
        form = CategoryForm(request.POST, instance=category)
        if form.is_valid():
            form.save()
            messages.success(request, 'Category updated successfully.')
            return redirect('view_categories')
    else:
        form = CategoryForm(instance=category)

    return render(request, 'edit_category.html', {
        'form': form,
        'category': category
    })


@login_required
def delete_category(request, pk):
    category = get_object_or_404(Category, pk=pk)
    category_name = category.name
    category.delete()
    messages.success(request, f"Category '{category_name}' deleted successfully.")
    return redirect('view_categories')


# ───────────────────────────────────────────────
# Income Views
# ───────────────────────────────────────────────

@login_required
def add_income(request):
    if request.method == 'POST':
        form = IncomeForm(request.POST)
        if form.is_valid():
            income = form.save(commit=False)
            income.user = request.user
            income.save()
            messages.success(request, 'Income added successfully.')
            return redirect('view_income')
    else:
        form = IncomeForm()

    return render(request, 'add_income.html', {'form': form})


@login_required
def view_income(request):
    incomes = Income.objects.filter(user=request.user)

    # Apply filters
    if start_date := request.GET.get('start_date'):
        incomes = incomes.filter(date__gte=start_date)
    if end_date := request.GET.get('end_date'):
        incomes = incomes.filter(date__lte=end_date)
    if min_amount := request.GET.get('min_amount'):
        incomes = incomes.filter(amount__gte=min_amount)
    if max_amount := request.GET.get('max_amount'):
        incomes = incomes.filter(amount__lte=max_amount)
    if source := request.GET.get('source'):
        incomes = incomes.filter(source__icontains=source)

    incomes = incomes.order_by('-date')

    return render(request, 'view_income.html', {'incomes': incomes})


@login_required
def export_income_csv(request):
    incomes = Income.objects.filter(user=request.user)

    # Same filters as view_income
    if start_date := request.GET.get('start_date'):
        incomes = incomes.filter(date__gte=start_date)
    if end_date := request.GET.get('end_date'):
        incomes = incomes.filter(date__lte=end_date)
    if min_amount := request.GET.get('min_amount'):
        incomes = incomes.filter(amount__gte=min_amount)
    if max_amount := request.GET.get('max_amount'):
        incomes = incomes.filter(amount__lte=max_amount)
    if source := request.GET.get('source'):
        incomes = incomes.filter(source__icontains=source)

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="income_data.csv"'

    writer = csv.writer(response)
    writer.writerow(['Date', 'Source', 'Amount', 'Note'])

    for income in incomes:
        writer.writerow([
            income.date,
            income.source,
            income.amount,
            income.note or ''
        ])

    return response


@login_required
def edit_income(request, pk):
    income = get_object_or_404(Income, pk=pk, user=request.user)

    if request.method == 'POST':
        form = IncomeForm(request.POST, instance=income)
        if form.is_valid():
            form.save()
            messages.success(request, 'Income updated successfully.')
            return redirect('view_income')
    else:
        form = IncomeForm(instance=income)

    return render(request, 'edit_income.html', {
        'form': form,
        'income': income
    })


@login_required
def delete_income(request, pk):
    income = get_object_or_404(Income, pk=pk, user=request.user)
    income.delete()
    messages.success(request, 'Income record deleted successfully.')
    return redirect('view_income')


# ───────────────────────────────────────────────
# Expense Views
# ───────────────────────────────────────────────

@login_required
def add_expense(request):
    if request.method == 'POST':
        form = ExpenseForm(request.POST)
        if form.is_valid():
            expense = form.save(commit=False)
            expense.user = request.user
            expense.save()
            messages.success(request, 'Expense added successfully.')
            return redirect('view_expense')
    else:
        form = ExpenseForm()

    return render(request, 'add_expense.html', {'form': form})


@login_required
def view_expense(request):
    expenses = Expense.objects.filter(user=request.user)

    # Apply filters if provided
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    min_amount = request.GET.get('min_amount')
    max_amount = request.GET.get('max_amount')
    category_name = request.GET.get('category')

    if start_date:
        expenses = expenses.filter(date__gte=start_date)
    if end_date:
        expenses = expenses.filter(date__lte=end_date)
    if min_amount:
        expenses = expenses.filter(amount__gte=min_amount)
    if max_amount:
        expenses = expenses.filter(amount__lte=max_amount)
    if category_name:
        expenses = expenses.filter(category__name__icontains=category_name)

    expenses = expenses.order_by('-date')

    return render(request, 'view_expense.html', {'expenses': expenses})


@login_required
def export_expense_csv(request):
    expenses = Expense.objects.filter(user=request.user)

    # Same filters
    if start_date := request.GET.get('start_date'):
        expenses = expenses.filter(date__gte=start_date)
    if end_date := request.GET.get('end_date'):
        expenses = expenses.filter(date__lte=end_date)
    if min_amount := request.GET.get('min_amount'):
        expenses = expenses.filter(amount__gte=min_amount)
    if max_amount := request.GET.get('max_amount'):
        expenses = expenses.filter(amount__lte=max_amount)
    if category_name := request.GET.get('category'):
        expenses = expenses.filter(category__name__icontains=category_name)

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="expense_data.csv"'

    writer = csv.writer(response)
    writer.writerow(['Date', 'Category', 'Amount', 'Note'])

    for expense in expenses:
        writer.writerow([
            expense.date,
            expense.category.name,
            expense.amount,
            expense.note or ''
        ])

    return response


@login_required
def edit_expense(request, pk):
    expense = get_object_or_404(Expense, pk=pk, user=request.user)

    if request.method == 'POST':
        form = ExpenseForm(request.POST, instance=expense)
        if form.is_valid():
            form.save()
            messages.success(request, 'Expense updated successfully.')
            return redirect('view_expense')
    else:
        form = ExpenseForm(instance=expense)

    return render(request, 'edit_expense.html', {
        'form': form,
        'expense': expense
    })


@login_required
def delete_expense(request, pk):
    expense = get_object_or_404(Expense, pk=pk, user=request.user)
    expense.delete()
    messages.success(request, 'Expense deleted successfully.')
    return redirect('view_expense')