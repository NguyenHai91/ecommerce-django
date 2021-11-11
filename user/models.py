
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager

# Create your models here.

class UserManager(BaseUserManager):
  def create_user(self, email, password, first_name=None, last_name=None):
    if not email:
      raise ValueError('User must have an email address')

    if not password:
      raise ValueError('User must have password')

    user = self.model(email=email, first_name=first_name, last_name=last_name)
    user.set_password(password)
    user.save(using=self._db)
    return user

  def create_superuser(self, email, password, first_name=None, last_name=None):
    user = self.create_user(
      email = self.normalize_email(email),
      password = password,
      first_name = first_name,
      last_name = last_name
    )
    user.is_admin = True
    user.is_staff = True
    user.is_superuser = True
    user.is_active = True
    user.save(using=self._db)



class User(AbstractBaseUser):
  first_name = models.CharField(max_length=100, null=True, blank=True)
  last_name = models.CharField(max_length=100, null=True, blank=True)
  email = models.EmailField(unique=True)
  password = models.CharField(max_length=200)
  phone = models.CharField(max_length=50)

  # required
  created_date = models.DateTimeField(auto_now_add=True)
  last_login = models.DateTimeField(auto_now=True)
  is_admin = models.BooleanField(default=False)
  is_staff = models.BooleanField(default=False)
  is_superadmin = models.BooleanField(default=False)
  is_active = models.BooleanField(default=True)

  class Meta:
    verbose_name = 'User'
    verbose_name_plural = 'Users'

  USERNAME_FIELD = 'email'
  REQUIRED_FIELDS = []

  objects = UserManager()

  def __str__(self) -> str:
    return self.email

  def has_perm(self, perm, obj=None):
    return self.is_admin

  def has_module_perms(self, add_label):
    return True
