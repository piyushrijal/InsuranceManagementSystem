from django.shortcuts import render, redirect, reverse
from . import forms, models
from django.db.models import Sum
from django.contrib.auth.models import Group
from django.http import HttpResponseRedirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.conf import settings
from datetime import date, timedelta
from django.db.models import Q
from django.core.mail import send_mail
from insurance import models as CMODEL
from insurance import forms as CFORM
from django.contrib.auth.models import User


def customerclick_view(request):
    if request.user.is_authenticated:
        return HttpResponseRedirect('afterlogin')
    return render(request, 'customer/customerclick.html')


def customer_signup_view(request):
    userForm = forms.CustomerUserForm()
    customerForm = forms.CustomerForm()
    mydict = {'userForm': userForm, 'customerForm': customerForm}

    if request.method == 'POST':
        userForm = forms.CustomerUserForm(request.POST)
        customerForm = forms.CustomerForm(request.POST, request.FILES)

        if userForm.is_valid() and customerForm.is_valid():
            user = userForm.save(commit=False)
            user.set_password(user.password)
            user.save()

            customer = customerForm.save(commit=False)
            customer.user = user
            customer.save()

            my_customer_group, created = Group.objects.get_or_create(name='CUSTOMER')
            my_customer_group.user_set.add(user)

            return HttpResponseRedirect('/login')
        else:
            # Include the form errors in the context
            mydict['userForm'] = userForm
            mydict['customerForm'] = customerForm

    return render(request, 'customer/customersignup.html', context=mydict)


def is_customer(user):
    return user.groups.filter(name='CUSTOMER').exists()


@login_required(login_url='customerlogin')
def customer_dashboard_view(request):
    dict = {
        'customer': models.Customer.objects.get(user_id=request.user.id),
        'available_policy': CMODEL.Policy.objects.all().count(),
        'applied_policy': CMODEL.PolicyRecord.objects.all().filter(
            customer=models.Customer.objects.get(user_id=request.user.id)).count(),
        'total_category': CMODEL.Category.objects.all().count(),
        'total_question': CMODEL.Question.objects.all().filter(
            customer=models.Customer.objects.get(user_id=request.user.id)).count(),
    }
    return render(request, 'customer/customer_dashboard.html', context=dict)


@login_required
def apply_policy_view(request):
    customer = models.Customer.objects.get(user_id=request.user.id)
    policies = CMODEL.Policy.objects.all()
    applied_policies = CMODEL.PolicyRecord.objects.filter(customer=customer).values_list('Policy_id', flat=True)
    return render(request, 'customer/apply_policy.html', {
        'policies': policies,
        'customer': customer,
        'applied_policies': applied_policies,
    })


@login_required
def apply_view(request, pk):
    customer = models.Customer.objects.get(user_id=request.user.id)
    policy = CMODEL.Policy.objects.get(id=pk)
    if not CMODEL.PolicyRecord.objects.filter(customer=customer, Policy=policy).exists():
        policyrecord = CMODEL.PolicyRecord(Policy=policy, customer=customer)
        policyrecord.save()
    return redirect('history')


def history_view(request):
    customer = models.Customer.objects.get(user_id=request.user.id)
    policies = CMODEL.PolicyRecord.objects.all().filter(customer=customer)
    return render(request, 'customer/history.html', {'policies': policies, 'customer': customer})


def ask_question_view(request):
    customer = models.Customer.objects.get(user_id=request.user.id)
    form = CFORM.QuestionForm()

    if request.method == 'POST':
        form = CFORM.QuestionForm(request.POST)
        if form.is_valid():
            question = form.save(commit=False)
            question.customer = customer
            question.save()
            return redirect('question-history')
    return render(request, 'customer/ask_question.html', {'form': form, 'customer': customer})


def question_history_view(request):
    customer = models.Customer.objects.get(user_id=request.user.id)
    questions = CMODEL.Question.objects.all().filter(customer=customer)
    return render(request, 'customer/question_history.html', {'questions': questions, 'customer': customer})
