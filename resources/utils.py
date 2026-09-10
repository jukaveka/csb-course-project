from django.contrib.auth.models import User
from .models import Resource
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

def get_all_resources(request_user):
    data = Resource.objects.filter(user=request_user, is_active=True)
    resources = [resource for resource in data.values("id", "name")]
    return resources

def get_filtered_resources(request_user, filter):
    user = User.objects.get(username=request_user)
    user_id = str(user.id)
    filteredData = Resource.objects.raw(
      """
      SELECT id, name
      FROM resources_resource
      WHERE is_active = True
      AND user_id = """ + str(user_id) + """
      AND name LIKE '%%""" + filter + """%%'
      """
    )

    return list(filteredData)

def get_filtered_resources_secure(request_user, filter):
    user = User.objects.get(username=request_user)
    user_id = str(user.id)
    filter = "%" + filter + "%"
    filteredData = Resource.objects.raw(
      """
      SELECT id, name
      FROM resources_resource
      WHERE is_active = True
      AND user_id = %s
      AND name LIKE %s
      """, [user_id, filter]
    )

    return list(filteredData)