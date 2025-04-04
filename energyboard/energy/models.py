from django.db import models

# Create your models here.
class EnergyData(models.Model):
    date = models.DateField()
    region = models.CharField(max_length=100)
    consumption_twh = models.FloatField()
    
    
    def __str__(self):
        return f"{self.date} -{self.region} - {self.consumption_twh} TWh"
    