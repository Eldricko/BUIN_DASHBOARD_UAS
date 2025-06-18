from django.db import models

# Create your models here.
# payment per bulan
from django.db import models

class TimeDimension(models.Model):
    year = models.IntegerField()
    month = models.IntegerField()

    class Meta:
        unique_together = ('year', 'month')

class PaymentMode(models.Model):
    name = models.CharField(max_length=50)

class PaymentPrediction(models.Model):
    time = models.ForeignKey(TimeDimension, on_delete=models.CASCADE)
    payment_mode = models.ForeignKey(PaymentMode, on_delete=models.CASCADE)
    actual_count = models.IntegerField()
    predicted_count = models.IntegerField()


#kategori produk terjual perbulan
class ProductCategory(models.Model):
    name = models.CharField(max_length=100)

class CategoryPrediction(models.Model):
    time = models.ForeignKey(TimeDimension, on_delete=models.CASCADE)
    category = models.ForeignKey(ProductCategory, on_delete=models.CASCADE)
    actual_quantity = models.IntegerField()
    predicted_quantity = models.IntegerField()


#produk terjual di kota perbulan
class City(models.Model):
    name = models.CharField(max_length=100)
    state = models.CharField(max_length=100)

class CitySalesPrediction(models.Model):
    time = models.ForeignKey(TimeDimension, on_delete=models.CASCADE)
    city = models.ForeignKey(City, on_delete=models.CASCADE)
    actual_quantity = models.IntegerField()
    predicted_quantity = models.IntegerField()

