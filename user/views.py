
from django.http.response import HttpResponse
from django.shortcuts import redirect, render
from django.contrib import messages, auth
from django.contrib.auth.decorators import login_required
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import EmailMessage
import requests

from .models import User
from .forms import RegistrationForm
from cart.views import _cart_id
from cart.models import Cart, CartItem


# Create your views here.

def register(request):
  if request.method == 'POST':
    form = RegistrationForm(request.POST)
    if form.is_valid():
      first_name = form.cleaned_data['first_name']
      last_name = form.cleaned_data['last_name']
      email = form.cleaned_data['email']
      phone = form.cleaned_data['phone']
      password = form.cleaned_data['password']

      new_user = User.objects.create_user(
        first_name=first_name,
        last_name=last_name,
        email=email,
        password=password
      )
      new_user.save()

      # user activation
      current_site = get_current_site(request)
      mail_subject = 'Please activate your account'
      message = render_to_string('accounts/user_verification_email.html', {
          'user': new_user,
          'domain': current_site,
          'uid': urlsafe_base64_encode(force_bytes(new_user.pk)),
          'token': default_token_generator.make_token(new_user),
      })
      to_email = email
      send_email = EmailMessage(mail_subject, message, to=[to_email])
      send_email.send()

      messages.success(request, 'Registration successful.')
      return redirect('user/login/?command=verification&email='+email)
    else:
      messages.error(request, form.errors)
      return redirect('register')

  form = RegistrationForm()
  context = {
    'form': form,
  }
  return render(request, 'accounts/register.html', context)


def login(request):
  if request.method == 'POST':
    email = request.POST['email']
    password = request.POST['password']
    user = auth.authenticate(email=email, password=password)

    if user is not None:
      try:
        cart = Cart.objects.get(cart_id=_cart_id(request))
        is_cart_item_exists = CartItem.objects.filter(cart=cart).exists()
        if is_cart_item_exists:
          cart_items = CartItem.objects.filter(cart=cart)
          product_variations = []
          for item in cart_items:
            variations = list(item.variations.all())
            product_variations.append(variations)

          cart_items = CartItem.objects.filter(user=user)
          ex_var_list = []
          id_list = []
          for item in cart_items:
            existing_variations = list(item.variations.all())
            ex_var_list.append(existing_variations)
            id_list.append(item.id)

          for variation in product_variations:
            print(variation)
            
            if variation in ex_var_list:
              index = ex_var_list.index(variation)
              item_id = id_list[index]
              item = CartItem.objects.filter(id=item_id).first()
              item.quantity += 1
              
              item.user = user
              item.save()
            else:
              cart_items = CartItem.objects.filter(cart=cart)
              for item in cart_items:
                item.user = user
                item.save()

          # for item in cart_items:
          #   item.user = user
          #   item.save()
      except:
        pass

      auth.login(request, user)
      url = request.META.get('HTTP_REFERER')
      try:
        query = requests.utils.urlparse(url).query
        params = dict(x.split('=') for x in query.split('&'))
        if 'next' in params:
          nextPage = params['next']
          return redirect(nextPage)
      except:
        return redirect('dashboard')
      
    else:
      messages.error(request, 'Login fail')
      return redirect('login')
  return render(request, 'accounts/login.html')


@login_required(login_url = 'login')
def logout(request):
  auth.logout(request)
  return redirect('home')


def activate(request, uidb64, token):
  try:
    uid = urlsafe_base64_decode(uidb64).decode()
    user = User._default_manager.get(pk=uid)
  except(TypeError, ValueError, OverflowError, User.DoesNotExist):
    user = None
  
  if user is not None and default_token_generator.check_token(user, token):
    user.is_active = True
    user.save()
    messages.success(request, 'Your email is activate!')
    return redirect('login')
  else:
    messages.error(request, 'Invalid activate link!')
    return redirect('register')


@login_required(login_url= 'login')
def dashboard(request):

  return render(request, 'accounts/dashboard.html')

def forgotPassword(request):
  if request.method == 'POST':
    email = request.POST['email']
    if User.objects.filter(email=email).exitsts():
      user = User.objects.get(email__exact=email)

      # Reset password
      current_site = get_current_site(request)
      mail_subject = 'Reset Your Password'
      message = render_to_string('accounts/reset_password_email.html', {
          'user': user,
          'domain': current_site,
          'uid': urlsafe_base64_encode(force_bytes(user.pk)),
          'token': default_token_generator.make_token(user),
      })
      to_email = email
      send_email = EmailMessage(mail_subject, message, to=[to_email])
      send_email.send()

      messages.success(request, 'Password reset email has been sent to your email address.')
      return redirect('login')
    else:
      messages.error(request, 'User does not exist!')
      return redirect('forgotPassword')

  return render(request, 'accounts/forgotPassword.html')


def forgotpassword_validate(request):
  messages.success(request, 'Validate password success')
  return redirect('login')


def resetPassword_validate(request, uidb64, token):
  try:
    uid = urlsafe_base64_decode(uidb64).decode()
    user = User._default_manager.get(pk=uid)
  except(TypeError, ValueError, OverflowError, User.DoesNotExist):
    user = None

  if user is not None and default_token_generator.check_token(user, token):
    request.session['uid'] = uid
    messages.success(request, 'Please reset your password.')
    return redirect('resetPassword')
  else:
    messages.error(request, 'This link has been expired.')
    return redirect('login')


def resetPassword(request):
  if request.method == 'POST':
    password = request.POST['password']
    confirm_password = request.POST['confirm_password']

    if password == confirm_password:
      uid = request.session.get('uid')
      user = User.objects.get(pk=uid)
      user.set_password(password)
      user.save()
      messages.success(request, 'Password reset successful.')
      return redirect('login')
    else:
      messages.error(request, 'Password do not match!')
      return redirect('resetPassword')
  else:
    return render(request, 'accounts/resetPassword.html')