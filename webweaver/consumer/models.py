from tortoise import Model, fields
from common.fields import EmailField

class Customer(Model):

    email = EmailField(max_length=255)