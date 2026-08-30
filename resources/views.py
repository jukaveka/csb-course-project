from django.shortcuts import render, redirect

from django.contrib.auth.models import User
from .models import Resource

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth.decorators import login_required

from django.core.exceptions import ValidationError
from django.db import IntegrityError

import requests
import os

@login_required
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


@login_required
def addView(request):
  if request.method == "POST":
    name = request.POST.get("name")
    url = request.POST.get("url")
    notes = request.POST.get("notes")

    ''' CHECK AND VALIDATIONS FOR URL (SSRF) '''

    response = requests.get(url=url)

    if response.status_code == 200:
      user = User.objects.get(username=request.user)
      file_name = name.replace(" ", "_")
      directory = "media/images/user/" + str(user.id)
      extension = response.headers["content-type"].split("/")[1]

      if os.path.exists(directory) == False:
          os.makedirs(directory)

      file_path = directory + "/" + file_name + "." + extension

      with open(file_path, "wb") as file:
        file.write(response.content)

      resource = Resource(name=name, url=url, notes=notes, file_path=file_path, user=request.user, is_active=True)
      resource.save()
      return redirect("resources")

    return redirect("home")

  if request.method == "GET":
    return render(request, "pages/add.html")


@login_required
def resourcesView(request):
  data = Resource.objects.filter(user=request.user, is_active=True)
  resources = [resource for resource in data.values("id", "name")]
  context = {
    "resources": resources
  }
  return render(request, "pages/list.html", context)


@login_required
def resourceView(request, resource_id):
  if request.method == "GET":
    resource = Resource.objects.get(pk=resource_id)
    resource.file_path = "/" + resource.file_path

    return render(request, "pages/resource.html", context={ "resource": resource })

  if request.method == "POST":
    resource = Resource.objects.get(pk=resource_id)
    resource.is_active = False
    resource.save()

    return redirect("resources")