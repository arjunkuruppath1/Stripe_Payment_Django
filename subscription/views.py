from django.http import HttpResponse
from django.contrib.auth.decorators import login_required,user_passes_test
from django.http import HttpResponse
from django.shortcuts import render,redirect
from .forms import CustomSignupForm
from django.urls import reverse_lazy
from django.views import generic
from django.contrib.auth import authenticate, login
from .models import Customer
import stripe


# def index(request):
#     return HttpResponse("Welcome to our Membership website")

def home(request):
    return render(request, 'subscription/home.html')

@login_required
def settings(request):
    membership = False
    cancel_at_period_end = False
    if request.method == 'POST':
        subscription = stripe.Subscription.retrieve(request.user.customer.stripe_subscription_id)
        subscription.cancel_at_period_end = True
        request.user.customer.cancel_at_period_end = True
        cancel_at_period_end = True
        subscription.save()
        request.user.customer.save()
    else:
        try:
            if request.user.customer.membership:
                membership = True
            if request.user.customer.cancel_at_period_end:
                cancel_at_period_end = True
        except Customer.DoesNotExist:
            membership = False
    return render(request, 'registration/settings.html', {'membership':membership,
    'cancel_at_period_end':cancel_at_period_end})


stripe.api_key = "sk_test_51LOauKSCMJBZdj5Zwit9T6fVWNXqi5aKyWfh3vsDS0TnUAffLp7PSEBdFjM6Hgo6bhCMhSurxE8pqMPijPP0Tx7q00XLWdK36T"


def join(request):
    return render(request, 'subscription/join.html')


def success(request):
    if request.method == 'GET' and 'session_id' in request.GET:
        session = stripe.checkout.Session.retrieve(request.GET['session_id'],)
        customer = Customer()
        customer.user = request.user
        customer.stripeid = session.customer
        customer.membership = True
        customer.cancel_at_period_end = False
        customer.stripe_subscription_id = session.subscription
        customer.save()
    return render(request, 'subscription/success.html')


def cancel(request):
    return render(request, 'subscription/cancel.html')


@login_required
def checkoutt(request):

    try:
        if request.user.customer.membership:
            return redirect('settings')
    except Customer.DoesNotExist:
        pass

    if request.method == 'POST':
        pass
    else:
        membership = 'monthly'
        final_dollar = 10
        membership_id = 'price_1LOd6KSCMJBZdj5ZfaGkBOW7'
        if request.method == 'GET' and 'membership' in request.GET:
            if request.GET['membership'] == 'yearly':
                membership = 'yearly'
                membership_id = 'price_1LOd6rSCMJBZdj5ZXWeIVK6V'
                final_dollar = 100

        # Create Strip Checkout
        session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            customer_email = request.user.email,
            line_items=[{
                'price': membership_id,
                'quantity': 1,
            }],
            mode='subscription',
            allow_promotion_codes=True,
            success_url='http://127.0.0.1:8000/success?session_id={CHECKOUT_SESSION_ID}',
            cancel_url='http://127.0.0.1:8000/cancel',
        )

        return render(request, 'subscription/checkout.html', {'final_dollar': final_dollar, 'session_id': session.id})

class SignUp(generic.CreateView):
    form_class = CustomSignupForm
    success_url = reverse_lazy('home')
    template_name = 'registration/signup.html'

    def form_valid(self, form):
        valid = super(SignUp, self).form_valid(form)
        username, password = form.cleaned_data.get('username'), form.cleaned_data.get('password1')
        new_user = authenticate(username=username, password=password)
        login(self.request, new_user)
        return valid



@user_passes_test(lambda u: u.is_superuser)
def updateaccounts(request):
    customers = Customer.objects.all()
    for customer in customers:
        subscription = stripe.Subscription.retrieve(customer.stripe_subscription_id)
        if subscription.status != 'active':
            customer.membership = False
        else:
            customer.membership = True
        customer.cancel_at_period_end = subscription.cancel_at_period_end
        customer.save()
    return HttpResponse('completed')