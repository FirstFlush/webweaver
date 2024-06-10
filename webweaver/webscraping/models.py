# This file is for scraped-data metadata such as countries, industries, states, etc.
# the ScrapeModel subclass of Model is also defined here.
import logging
from pathlib import Path
from pypostalcode import PostalCodeDatabase
from tortoise import Model, fields
from tortoise.exceptions import DoesNotExist, IntegrityError, TransactionManagementError
from tortoise.transactions import in_transaction
from typing import Awaitable, Type, TypeVar

from webweaver.common.enums import CountryEnum
# from common.fields import URLField, EmailField
from webweaver.exceptions import CountryNotFound
from webweaver.webscraping.registry.scraping_registry import scraping_registry

logger = logging.getLogger('scraping')
T = TypeVar('T', bound='ScrapeModel')


def get_scrape_job() -> int | None:
    try:
        return scraping_registry.scrape_job.id
    except AttributeError:
        return


class ScrapeModel(Model):
    """All scraped data will be subclassed from the ScrapeModel table class."""
    # spider = fields.ForeignKeyField("models.SpiderAsset", default=get_spider_asset)
    scrape_job_id = fields.ForeignKeyField("models.ScrapeJob", default=get_scrape_job, null=True)

    class Meta:
        abstract = True

    @classmethod
    def table_name(cls) -> str:
        """Returns the table's name"""
        return cls.__name__


    @classmethod
    async def get_create_or_update(cls:Type[T], **kwargs) -> tuple[T, bool, bool]:
        """This method assumes kwargs will ALWAYS contain every unique constraint field.
        If a unique constraint is present on the model, but it's field name is not present
        in kwargs then it can lead to unexpected results.

        Returns a tuple of (obj, created, updated)
        """
        unique_constraints = cls._unique_constraints_set()
        cls._validate_unique_constraints(kwargs, unique_constraints)
        filter_dict = {field: kwargs[field] for field in unique_constraints if field in kwargs}
        db = cls._choose_db(True)
        created = False
        updated = False
        async with in_transaction(connection_name=db.connection_name) as connection:
            try:
                obj = await cls.select_for_update().filter(**filter_dict).using_db(connection).get()
            except DoesNotExist:
                try:
                    obj = await cls.create(using_db=connection, **kwargs)
                    created = True
                    return obj, created, updated
                except (IntegrityError, TransactionManagementError) as e:
                    msg = f"{e.__class__.__name__} on {cls.__name__}: Possible race condition!"
                    logger.warning(f"{e}: {msg}")
                    print()
                    print('KWARGS: ', kwargs)
                    print()
                    obj = await cls.filter(**filter_dict).using_db(connection).get()
            for field_name, field_value in kwargs.items():
                if hasattr(obj, field_name) and getattr(obj, field_name) != field_value:
                    setattr(obj, field_name, field_value)
                    updated = True
            if updated:
                await obj.save()
            return obj, created, updated


    @classmethod
    def _validate_unique_constraints(cls, kwargs: dict, unique_constraints: set):
        """This method ensures that every unique constraint in unique_constraints
        is also present in the kwargs dict.
        """
        missing_fields = unique_constraints - kwargs.keys()
        if missing_fields:
            raise ValueError(f"Missing unique constraint fields: `{', '.join(missing_fields)}` for model `{cls.__name__}`")


    @classmethod
    async def update_row(cls, obj, **kwargs):
        for field_name, field_value in kwargs.items():
            if hasattr(obj, field_name):
                setattr(obj, field_name, field_value)
        await obj.save()



    @classmethod
    def _unique_constraints_set(cls) -> set:
        """Returns all unique constraint fields as a set"""
        unique_constraints_set = set()
        unique_constraints = cls._unique_constraints()
        for constraint_tuple in unique_constraints:
            for field_name in constraint_tuple:
                if not field_name.endswith('_id'):
                    unique_constraints_set.add(field_name)
        return unique_constraints_set



    @classmethod
    def _unique_constraints(cls, include_generated:bool=False) -> list[tuple[str]]:
        """Returns the unique constraints (except id) in the form of a
        list of tuples. This will catch singular unique constraints (fields defined
        with unique=True) and also combined unique constraints defined in
        the class Meta with the unique_together attribute.

        include_generated=True will include automatically-generated fields
        such as 'id'.
        """
        unique_constraints = []
        for field_name, field_object in cls._meta.fields_map.items():
            if include_generated:
                if field_object.unique:
                    unique_constraints.append((field_name,))
            else:
                if field_object.unique and not field_object.generated:  #not id
                    unique_constraints.append((field_name,))
        if hasattr(cls._meta, 'unique_together') and cls._meta.unique_together:
            for unique_constraint in cls._meta.unique_together:
                unique_constraints.append(unique_constraint)
        return unique_constraints


    # @staticmethod
    # def get_country_enum(country_name:str) -> CountryEnum:
    #     """Get the CountryEnum object based on the country name."""
    #     try:
    #         return CountryEnum[country_name.upper()]
    #     except KeyError:
    #         raise ValueError(f"No country ISO found for: {country_name}")


    # @classmethod
    # async def get_country(cls, country_name:str) -> Awaitable["Country"] | None:
    #     """Gets the country object associated with the country name."""
    #     try:
    #         country_enum = cls.get_country_enum(country_name)
    #     except ValueError:
    #         logger.error(CountryNotFound(country_name))
    #         return None
    #     else:
    #         return await Country.get_country(country_enum)


# class Country(Model):
#     iso_code = fields.CharEnumField(enum_type=CountryEnum, max_length=3, unique=True) # Alpha-3 ISO code


#     @classmethod
#     async def get_country(cls, country:CountryEnum) -> Awaitable["Country"]:
#         """Retrieves the Country object based on the CountryEnum you pass in."""
#         country_code = country.value
#         return await Country.get(iso_code=country_code)


#     def country_name(self) -> str:
#         """Returns the country name"""
#         return self.iso_code.name
    

#     @classmethod
#     def get_name(cls) -> str:
#         """Returns the table's name"""
#         return cls.__name__




# class Industry(Model):
#     industry_name = fields.CharField(max_length=255, unique=True)
#     common_names = fields.TextField(null=True)


#     @classmethod
#     def get_name(cls) -> str:
#         """Returns the table's name"""
#         return cls.__name__


# class IndustryAlias(Model):
#     industry_id = fields.ForeignKeyField("models.Industry", related_name="aliases")
#     alias = fields.CharField(max_length=255)



