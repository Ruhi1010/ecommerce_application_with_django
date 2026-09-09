from django.db import models

# Create your models here.
from base.models import BaseModel
from django.utils.text import slugify


class Category(BaseModel):
    category_name = models.CharField(max_length=255)
    slug = models.SlugField(unique=True, null=True, blank=True)
    category_image = models.ImageField(upload_to = "categories")

    
    
    def save(self, *args, **kwargs):
            self.slug = slugify(self.category_name)
            super(Category, self).save(*args, **kwargs)
            
            
            
            
    def __str__(self):
            return self.category_name
    
    
    


class ColorVariation(BaseModel):
    color_name = models.CharField(max_length=100)
    price = models.IntegerField(default=0)
    
    
    def __str__(self):
            return self.color_name
    


class SizeVariation(BaseModel):
    size_name = models.CharField(max_length=100)    
    price = models.IntegerField(default=0)
    
    
    def __str__(self):
            return self.size_name
  
    
    
    


class Product(BaseModel):
    product_name = models.CharField(max_length=255)
    slug = models.SlugField(unique=True, null=True, blank=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name="products")
    price = models.IntegerField()
    product_description = models.TextField()
    color_variation = models.ManyToManyField(ColorVariation, blank=True)
    size_variation = models.ManyToManyField(SizeVariation, blank=True)
    
    
    def save(self, *args, **kwargs):
                self.slug = slugify(self.product_name)
                super(Product, self).save(*args, **kwargs)
                
                
                
                
    def __str__(self):
                return self.product_name
    
    
    
    
  
    

class ProductImage(BaseModel):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="product_images")
    image = models.ImageField(upload_to="product")
    # product_description = models.TextField()
    
