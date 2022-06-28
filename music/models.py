from django.db import models

class Band(models.Model):
	name = models.CharField(max_length=50)

	class Meta:
		verbose_name = "Groupe"
		ordering = ['name']

	def __str__(self):
		return self.name


class Album(models.Model):
	code = models.CharField(max_length=20)
	band = models.ForeignKey('Band', on_delete=models.CASCADE, related_name='band')
	title = models.CharField(max_length=100)
	release_year = models.IntegerField(null=True, blank=True)
	score = models.IntegerField(null=True, blank=True)

	class Meta:
		unique_together = ('code',)
		ordering= ('release_year',)

	def __str__(self):
		return f'{self.band.name} - {self.title} '


class Track(models.Model):
	album = models.ForeignKey(Album, related_name='tracks', on_delete=models.CASCADE)
	order = models.IntegerField()
	title = models.CharField(max_length=100)

	class Meta:
		ordering= ('order',)
	
	def __str__(self):
		return f'{self.order} - {self.title}'