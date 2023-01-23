defaults = {
  "can_view_admin": False,
  "can_view_user": True,
  "can_use_pass": True,
  "can_view_dev": False,
  "can_submit_issues": False
}


class Permission:

  def __init__(self, **kwargs):
    for i in defaults:  #Make sure we have defaults
      setattr(self, i, defaults[i])
    for i in kwargs:  #Allow changing the defaults
      setattr(self, i, kwargs[i])

  def dict(self):
    dict = {}
    for i in dir(self):
      if not i.startswith("__") and not callable(self.__getattribute__(i)):
        dict[i] = self.__getattribute__(i)
    return dict

  def load_dict(self, dict):
    for i in dict:
      self.__setattr__(i, dict[i])


perms = {
  "user":
  Permission(),
  "dev":
  Permission(can_view_admin=True, can_view_dev=True, can_submit_issues=True),
  "admin":
  Permission(can_view_admin=True, can_submit_issues=True),
  "tester":
  Permission(can_submit_issues=True)
}


def get_permissions(perm):
  perm = perm.lower()
  if perm not in perms:
    return perms["user"]  #Default to user perms
  else:
    return perms[perm]
