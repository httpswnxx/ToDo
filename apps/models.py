from django.contrib.auth.models import  AbstractUser
from django.db.models import Model, CharField, ForeignKey, CASCADE, DateTimeField, BooleanField, DateField
from django.db.models.enums import TextChoices


class User(Model):
    username = CharField(max_length=100, unique=True)

    def __str__(self):
        return self.username

class Category(Model):
    title = CharField(max_length=100)
    user=ForeignKey(User,on_delete=CASCADE)
    created_at = DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

class Task(Model):
    title = CharField(max_length=100)
    category = ForeignKey(Category,on_delete=CASCADE,related_name='tasks')
    user=ForeignKey(User,on_delete=CASCADE,related_name='tasks')
    complete = BooleanField(default=False)
    created_at = DateTimeField(auto_now_add=True)
    due_date = DateField(null=True, blank=True)

    def __str__(self):
        return self.title