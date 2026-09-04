from django.db import models

# Create your models here.
from base.models import BaseModel


class Category(BaseModel):
    category_name = models.CharField(max_length=255)
    category_image = models.ImageField(upload_to = "categories")



class Product(BaseModel):
    product_name = models.CharField(max_length=255)
    category = models.ForeignKey(Category, on_delete=models.CASECADE, related_name="products")
    price = models.IntegerField()
    
    
    
    

class ProductImage(BaseModel):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="product_images")
    image = models.ImageField(upload_to="product")
    product_description = models.TextField()
    
