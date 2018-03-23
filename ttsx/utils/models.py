from django.db import models
class BaseModel(models.Model):
    add_date=models.DateTimeField(auto_now_add=True)
    update_date=models.DateTimeField(auto_now_add=True)
    isDelete=models.BooleanField(default=False)

    class Meta:
        abstract=True