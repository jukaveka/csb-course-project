from django.shortcuts import render, redirect

from django.contrib.auth.models import User
from .models import Resource
from .utils import get_path_file_type, get_user_directory, get_file_path, get_all_resources, get_filtered_resources, get_filtered_resources_secure

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth.decorators import login_required

from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.db.models import Model

from urllib.request import urlopen, Request
from urllib.error import URLError
from urllib.parse import urlsplit
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
      return render(request, "pages/signup.html", context={"error": "Passwords do not match"}, content_type="text/html", status=400)

    '''
    try:
      validate_password(password)
    except ValidationError as err:
      print(err)
      return render(request, "pages/signup.html", context={"error": "Weak password"}, content_type="text/html", status=400)
    '''

    try:
      user = User.objects.create_user(username, None, password)
      login(request, user)
    except IntegrityError as err:
      print("Integrity error", err.args)
      return render(request, "pages/signup.html", context={"error": "Username already in use"}, content_type="text/html", status=400)

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

    url_components = urlsplit(url)
    file_type = get_path_file_type(url_components.path)

    if url_components.scheme not in ["http", "https"] or file_type != "image":
      return render(request, "pages/add.html", { "error": "Invalid URL" }, status=400)

    try:
      image_request = Request(url)
      image_request.add_header("User-Agent", "Mozilla/5.0")
      image_response = urlopen(image_request)
      content = image_response.read()
    except URLError as err:
      print(err.reason)
      return render(request, "pages/add.html", { "error": "There was an issue with fetching image from the URL. Please confirm URL given is valid" }, status=400)

    directory = get_user_directory(request.user)
    file_path = get_file_path(name, directory, image_response.headers["content-type"])

    if os.path.exists(directory) == False:
        os.makedirs(directory)

    with open(file_path, "wb") as file:
      file.write(content)

    try:
      resource = Resource(name=name, url=url, notes=notes, file_path=file_path, user=request.user, is_active=True)
      resource.save()
      return redirect("resources")
    except err:
      print(err)
      return render(request, "pages/add.html", { "error": "There was an issue with saving the resource" })

  if request.method == "GET":
    return render(request, "pages/add.html")


@login_required
def resourcesView(request):
  filter = request.GET.get("filter")
  if filter == None:
    resources = get_all_resources(request.user)
  else:
    resources = get_filtered_resources(request.user, filter)

    '''
    Raw SQL utility function where filter is passed as parameter
    resources = get_filtered_resources_secure(request.user, filter)

    or

    Django ORM query including filter
    resources = list(Resource.objects.filter(user=request.user, is_active=True, name__icontains=filter))
    '''

  context = {
    "resources": resources
  }

  return render(request, "pages/list.html", context)


@login_required
def resourceView(request, resource_id):
  if request.method == "GET":

    try:
      resource = Resource.objects.get(pk=resource_id, is_active=True)

      '''
      resource = Resource.objects.get(pk=resource_id, user=request.user, is_active=True)
      '''

    except Resource.DoesNotExist as err:
      print(err.args)
      return render(request, "pages/list.html", context={ "error": "Resource not found" }, status=404)

    resource.file_path = "/" + resource.file_path

    return render(request, "pages/resource.html", context={ "resource": resource })

  if request.method == "POST":
    try:
      resource = Resource.objects.get(pk=resource_id, user=request.user, is_active=True)
    except Resource.DoesNotExist as err:
      print(err.args)
      return render(request, "pages/list.html", context={ "error": "Resource could not be deleted" })

    resource.is_active = False
    resource.save()

    return redirect("resources")