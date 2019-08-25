from django.db import models

import datetime

# Create your models here.

class Domain(models.Model):
	name = models.CharField(max_length=100)
	popularity_feedback = models.IntegerField(default=0)
	release_frequency_feedback = models.IntegerField(default=0)
	issue_closing_time_feedback = models.IntegerField(default=0)
	issue_response_time_feedback = models.IntegerField(default=0)
	performance_feedback = models.IntegerField(default=0)
	security_feedback = models.IntegerField(default=0)
	last_modification_date_feedback = models.IntegerField(default=0)
	backwards_compatibility_feedback = models.IntegerField(default=0)
	last_discussed_so_feedback = models.IntegerField(default=0)
	license_feedback = models.IntegerField(default=0)
	overall_score_feedback = models.IntegerField(default=0)

class Library(models.Model):
	name = models.CharField(max_length=100)
	tag = models.CharField(max_length=100)
	repository = models.CharField(max_length=100, default="None")
	popularity = models.IntegerField(default=0)
	release_frequency = models.FloatField(default=0)
	issue_closing_time = models.FloatField(default=0)
	issue_response_time = models.FloatField(default=0)
	performance = models.FloatField(default=0)
	security = models.FloatField(default=0)
	last_modification_dates = models.CharField(max_length=200, default=0)
	last_modification_date = models.DateTimeField(default=None,null=True, blank=True)
	backwards_compatibility = models.FloatField(default=0)
	breaking_changes = models.IntegerField(default=0)
	non_breaking_changes = models.IntegerField(default=0)
	last_discussed_so_dates = models.CharField(max_length=200, default=0)
	last_discussed_so = models.DateTimeField(default=None, null=True, blank=True)
	license = models.CharField(max_length=100, default="None")
	overall_score = models.FloatField(default=0)
	domain = models.ForeignKey(Domain, on_delete=models.CASCADE)  #This means that a domain can have several libraries

class Data(models.Model):
	name = models.CharField(max_length=100)
	tag = models.CharField(max_length=100)
	repository = models.CharField(max_length=100, default="None")
	popularity = models.IntegerField(default=0)
	release_frequency = models.FloatField(default=0)
	issue_closing_time = models.FloatField(default=0)
	issue_response_time = models.FloatField(default=0)
	performance = models.FloatField(default=0)
	security = models.FloatField(default=0)
	last_modification_dates = models.CharField(max_length=200, default=0)
	last_modification_date = models.DateTimeField(default=None,null=True, blank=True)
	backwards_compatibility = models.FloatField(default=0)
	breaking_changes = models.IntegerField(default=0)
	non_breaking_changes = models.IntegerField(default=0)
	last_discussed_so_dates = models.CharField(max_length=200, default=0)
	last_discussed_so = models.DateTimeField(default=None, null=True, blank=True)
	license = models.CharField(max_length=100, default="None")
	overall_score = models.FloatField(default=0)
	month = models.IntegerField(default=0)
	year = models.IntegerField(default=0)	
	run_time = models.DateField(default=None, null=True, blank=True)
	library = models.ForeignKey(Library, on_delete=models.CASCADE)
        #This means that a domain can have several libraries
	domain = models.ForeignKey(Domain, on_delete=models.CASCADE)

class Issue(models.Model):
	#This means that a library can have several issues
	library = models.ForeignKey(Library, on_delete=models.CASCADE)
	issue_id = models.CharField(max_length=20)
	title = models.CharField(max_length=500)
	performance_issue = models.BooleanField()
	security_issue = models.BooleanField()
	creation_date = models.DateTimeField()
	closing_date = models.DateTimeField(default=None, blank=True, null=True)
	first_response_date = models.DateTimeField(default=None, blank=True, null=True)

class Release(models.Model):
	#This means that a library can have several releases
	library = models.ForeignKey(Library, on_delete=models.CASCADE)
	name = models.CharField(max_length=100)
	release_date = models.DateTimeField()
	breaking_changes = models.IntegerField()

class Feedback(models.Model):
        text = models.CharField(max_length=500)
