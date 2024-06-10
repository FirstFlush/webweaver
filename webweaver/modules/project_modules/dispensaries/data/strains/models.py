import re

from tortoise.models import Model
from tortoise import fields
   
from webweaver.modules.project_modules.dispensaries.data.strains.enum import CannabisTypeEnum


class Breeder(Model):
    breeder = fields.CharField(max_length=255, unique=True)
   

class Ailment(Model):
    ailment = fields.CharField(max_length=255, unique=True)


class Flavor(Model):
    flavor = fields.CharField(max_length=255, unique=True)


class Effect(Model):
    effect = fields.CharField(max_length=255, unique=True)


class Strain(Model):
    name        = fields.CharField(max_length=255, unique=True)
    strain_type = fields.CharEnumField(CannabisTypeEnum)  # Indica, Sativa, Hybrid, Unknown
    breeder     = fields.ForeignKeyField('models.Breeder', related_name='strains', on_delete=fields.SET_NULL, null=True)
    ailments    = fields.ManyToManyField('models.Ailment', related_name='strains')
    effects     = fields.ManyToManyField('models.Effect', related_name='strains')
    flavors     = fields.ManyToManyField('models.Flavor', related_name='strains')
    date_added  = fields.DatetimeField(auto_now_add=True)


