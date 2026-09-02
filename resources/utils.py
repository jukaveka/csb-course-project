from django.contrib.auth.models import User
from mimetypes import guess_extension, types_map

def get_path_file_type(path):
  path_file_extension = "." + path.split(".")[-1]
  mime_type = types_map[path_file_extension]
  file_type = mime_type.split("/")[0]

  return file_type

def get_user_directory(username):
  user = User.objects.get(username=username)
  directory = "media/images/user/" + str(user.id) + "/"

  return directory

def get_file_path(resource_name, user_directory, content_type):
  file_name = resource_name.replace(" ", "_").lower()
  extension = guess_extension(content_type)
  file_path = user_directory + file_name + extension

  return file_path