from django.db import models

import datetime

from django.contrib.auth.models import PermissionsMixin
from django.contrib.auth.base_user import AbstractBaseUser
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.base_user import BaseUserManager

from django.conf import settings

from django.db.models.signals import post_save
from django.dispatch import receiver
from rest_framework.authtoken.models import Token

# Create your models here.

# A list of all library domains available
# feedback data about them (i.e., thumbs up, down from the website)
class Domain(models.Model):
	name = models.CharField(max_length=100)
	popularity_feedback = models.IntegerField(default=0,blank=True, null=True)
	release_frequency_feedback = models.IntegerField(default=0,blank=True, null=True)
	issue_closing_time_feedback = models.IntegerField(default=0,blank=True, null=True)
	issue_response_time_feedback = models.IntegerField(default=0,blank=True, null=True)
	performance_feedback = models.IntegerField(default=0,blank=True, null=True)
	security_feedback = models.IntegerField(default=0,blank=True, null=True)
	last_modification_date_feedback = models.IntegerField(default=0,blank=True, null=True)
	backwards_compatibility_feedback = models.IntegerField(default=0,blank=True, null=True)
	last_discussed_so_feedback = models.IntegerField(default=0,blank=True, null=True)
	license_feedback = models.IntegerField(default=0,blank=True, null=True)
	overall_score_feedback = models.IntegerField(default=0,blank=True, null=True)

	class Meta:
		db_table = "Domain"

	def __str__(self):
		return self.name


# A list of all libraries available
class Library(models.Model):
	name = models.CharField(max_length=100, unique=True)
	so_tag = models.CharField(max_length=100)
	github_repo = models.CharField(max_length=100, unique=True)
	github_url = models.CharField(max_length=200, default="None")
	jira_url = models.CharField(max_length=300, default="None")
	maven_url = models.CharField(max_length=200, default="None")
	package = models.CharField(max_length=100, default="None")

	#This means that a domain can have several libraries
	domain = models.ForeignKey(Domain, on_delete=models.CASCADE, related_name='libraries')

	class Meta:
		db_table = "Library"

	def __str__(self):
		return '{} from {}'.format(self.name, self.domain__name)

	@property
	def latest_metrics(self):
		return self.metrics.latest('created_on')

# The actual metric data
# To be able to show changes in metrics over time, each library can have multiple
# recorded entries. Typically, an entry is created every month
class MetricsEntry(models.Model):

	#This means that a library can have several data entries
	library = models.ForeignKey(Library, on_delete=models.CASCADE,related_name='metrics')

	popularity = models.IntegerField(default=0)
	release_frequency = models.FloatField(default=0)
	issue_closing_time = models.FloatField(default=0)
	issue_response_time = models.FloatField(default=0)
	performance = models.FloatField(default=0)
	security = models.FloatField(default=0)
	last_modification_dates = models.CharField(max_length=1000, default=0)
	last_modification_date = models.DateTimeField(default=None,null=True, blank=True)
	backwards_compatibility = models.FloatField(default=0)
	breaking_changes = models.IntegerField(default=0,null=True)
	non_breaking_changes = models.IntegerField(default=0,null=True)
	last_discussed_so_dates = models.CharField(max_length=1000, default=0,null=True)
	last_discussed_so = models.DateTimeField(default=None, null=True, blank=True)
	license = models.CharField(max_length=100, default="None")
	overall_score = models.FloatField(default=0)
	created_on = models.DateTimeField(auto_now_add=True)

	class Meta:
		db_table = "MetricsEntry"

		get_latest_by = "-created_on"

class Issue(models.Model):
	#This means that a library can have several issues
	library = models.ForeignKey(Library, on_delete=models.CASCADE, related_name='issues')
	issue_id = models.CharField(max_length=20)
	title = models.CharField(max_length=500)
	performance_issue = models.BooleanField()
	security_issue = models.BooleanField()
	creation_date = models.DateTimeField()
	closing_date = models.DateTimeField(default=None, blank=True, null=True)
	first_response_date = models.DateTimeField(default=None, blank=True, null=True)

	class Meta:
		db_table = "Issue"

class LibraryRelease(models.Model):
	#This means that a library can have several releases
	library = models.ForeignKey(Library, on_delete=models.CASCADE, related_name='releases')
	name = models.CharField(max_length=100)
	release_date = models.DateTimeField()
	breaking_changes = models.IntegerField(default=0)
	non_breaking_changes = models.IntegerField(default=-1, null=True)
	class Meta:
		db_table = "LibraryRelease"

#open-ended feedback from the website
class WebsiteFeedback(models.Model):
	text = models.CharField(max_length=500)

	class Meta:
		db_table = "WebsiteFeedback"

#tables related to plugin
class ProjectType(models.Model):
	project_type = models.CharField(max_length=100)

	def __str__(self):
		return self.project_type

	class Meta:
		db_table = "ProjectType"	

class TeamType(models.Model):
	team_type = models.CharField(max_length=100)

	def __str__(self):
		return self.team_type

	class Meta:
		db_table = "TeamType"

class Metric(models.Model):
	name = models.CharField(max_length=100)
	
	def __str__(self):
		return self.name
	
	class Meta:
		db_table = "Metric"

class UserManager(BaseUserManager):
    use_in_migrations = True

    def _create_user(self, username, **extra_fields):
        """
        Creates and saves a User with the given email and password.
        """
        if not username:
            raise ValueError('The username must be set')
        user = self.model(username=username, **extra_fields)
        user.set_password(PluginUser.objects.make_random_password())
        user.save(using=self._db)
        return user

    def create_user(self, username, **extra_fields):
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(username, **extra_fields)

    def create_superuser(self, username, **extra_fields):
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self._create_user(username, **extra_fields)

class PluginUser(AbstractBaseUser, PermissionsMixin):
	username = models.CharField(max_length=50, unique=True)
	occupation = models.CharField(max_length=100, blank=True, default="", null=True)
	programming_skills = models.IntegerField(default=0,blank=True, null=True) #high, low etc?
	java_skills = models.IntegerField(default=0,blank=True, null=True) #high, low etc?
	projects = models.ManyToManyField(ProjectType, related_name="users_with_proj_type", blank=True) #a user could work with multiple types of projects
	teams = models.ManyToManyField(TeamType, related_name="users_with_team_type", blank=True) #a user could work in multiple types of teams
	plugin_rating = models.IntegerField(default=0,blank=True, null=True) #1 to 5 stars
	optional_feedback = models.CharField(max_length=300, blank=True, default="", null=True)

	objects = UserManager()

	USERNAME_FIELD = 'username'
	REQUIRED_FIELDS = []

	class Meta:
		db_table = "PluginUser"

@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_auth_token(sender, instance=None, created=False, **kwargs):
    if created:
        Token.objects.create(user=instance)


class PluginFeedback(models.Model):
	user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, default=-1)
	from_library = models.ForeignKey(Library, on_delete=models.CASCADE, related_name="comparisons", default=-1) #original library
	to_library = models.ForeignKey(Library, on_delete=models.CASCADE,related_name="replacements",default=-1) #replaced lib (or empty if decided against replacing)
	action_date = models.DateTimeField(null=True)
	line_num = models.IntegerField(default=-1)
	project_name = models.CharField(max_length=100,null=True)
	class_name = models.CharField(max_length=100, null=True)
	full_lib_list = models.CharField(max_length=200, default="") #comma separated list of lib names for now

	class Meta:
		db_table = "PluginFeedback"

class Chart(models.Model):
	domain = models.ForeignKey(Domain, on_delete=models.CASCADE, related_name="charts")
	metric = models.ForeignKey(Metric, on_delete=models.CASCADE, related_name="charts", default=None)
	chart = models.BinaryField()
	
	class Meta:
		db_table = "Chart"
