from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.db import IntegrityError

def homeView(request):
  if request.user.is_authenticated:
    return render(request, "pages/home.html")
  else:
    return redirect("login")

def loginView(request):
  if request.method == "POST":
    username = request.POST.get("username")
    password = request.POST.get("password")

    user = authenticate(request, username=username, password=password)

    if user is not None:
      login(request, user)
      return redirect("home")
    else:
      return render(request, "pages/login.html", {"error": "login failed"})

  if request.method == "GET":
    return render(request, "pages/login.html")

def signupView(request):
  if request.method == "POST":
    username = request.POST.get("username")
    password = request.POST.get("password")
    passwordVerify = request.POST.get("passwordVerify")

    if password != passwordVerify:
      return render(request, "pages/signup.html", context={"error": "Passwords do not match"}, content_type="text/html")

    '''
    try:
      validate_password(password)
    except ValidationError as err:
      print(err)
      return render(request, "pages/signup.html", context={"error": "Weak password"}, content_type="text/html")
    '''

    try:
      user = User.objects.create_user(username, None, password)
      login(request, user)
    except IntegrityError as err:
      print("Integrity error", err.args)
      return render(request, "pages/signup.html", context={"error": "Username already in use"}, content_type="text/html")

    return redirect("home")

  if request.method == "GET":
    return render(request, "pages/signup.html")

def logoutView(request):
  logout(request)
  return redirect("login")