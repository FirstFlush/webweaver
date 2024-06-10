# from thefuzz import fuzz, process

from fuzzywuzzy import fuzz, process

from tortoise import Tortoise, run_async
from webweaver.config import POSTGRES_DB

from webweaver.modules.project_modules.dispensaries.data.strains.models import (
    Strain,
    Ailment,
    Effect,
    Flavor,
    Breeder,
)


async def main():

    await Tortoise.init(
        db_url=POSTGRES_DB,
        modules={'models': ['__main__']}
    )

    test_string = Strain.fuzzy_preprocess("motorbreath #2")

    strains = await Strain.all()
    strain_names = [Strain.fuzzy_preprocess(strain.name) for strain in strains]


    matches = process.extract(
        query=test_string, 
        choices=strain_names,
        scorer=fuzz.WRatio,
        limit=5,
        # processor=process.default_processor
    )
    print(matches)


run_async(main())
















# ratio = fuzz.ratio("zzaz", "aaaa")
# # print(ratio)

# choices = ['new york jets', 'NEW YORK GIANTS', 'New York Yankees', 'NEW yORk KnicKS']
# query = process.extract('NEW YORK blessed', choices, limit=1)
# print(query)


industries = [
    'Accounting',
    'Airlines/Aviation',
    'Alternative Dispute Resolution',
    'Alternative Medicine',
    'Animation',
    'Apparel & Fashion',
    'Architecture & Planning',
    'Arts & Crafts',
    'Automotive',
    'Aviation & Aerospace',
    'Banking',
    'Biotechnology',
    'Broadcast Media',
    'Building Materials',
    'Business Supplies & Equipment',
    'Capital Markets',
    'Chemicals',
    'Civic & Social Organization',
    'Civil Engineering',
    'Commercial Real Estate',
    'Computer & Network Security',
    'Computer Games',
    'Computer Hardware',
    'Computer Networking',
    'Computer Software',
    'Construction',
    'Consumer Electronics',
    'Consumer Goods',
    'Consumer Services',
    'Cosmetics',
    'Dairy',
    'Defense & Space',
    'Design',
    'Education Management',
    'E-learning',
    'Electrical & Electronic Manufacturing',
    'Entertainment',
    'Environmental Services',
    'Events Services',
    'Executive Office',
    'Facilities Services',
    'Farming',
    'Financial Services',
    'Fine Art',
    'Fishery',
    'Food & Beverages',
    'Food Production',
    'Fundraising',
    'Furniture',
    'Gambling & Casinos',
    'Glass, Ceramics & Concrete',
    'Government Administration',
    'Government Relations',
    'Graphic Design',
    'Health, Wellness & Fitness',
    'Higher Education',
    'Hospital & Health Care',
    'Hospitality',
    'Human Resources',
    'Import & Export',
    'Individual & Family Services',
    'Industrial Automation',
    'Information Services',
    'Information Technology & Services',
    'Insurance',
    'International Affairs',
    'International Trade & Development',
    'Internet',
    'Investment Banking/Venture',
    'Investment Management',
    'Judiciary',
    'Law Enforcement',
    'Law Practice',
    'Legal Services',
    'Legislative Office',
    'Leisure & Travel',
    'Libraries',
    'Logistics & Supply Chain',
    'Luxury Goods & Jewelry',
    'Machinery',
    'Management Consulting',
    'Maritime',
    'Marketing & Advertising',
    'Market Research',
    'Mechanical or Industrial Engineering',
    'Media Production',
    'Medical Device',
    'Medical Practice',
    'Mental Health Care',
    'Military',
    'Mining & Metals',
    'Motion Pictures & Film',
    'Museums & Institutions',
    'Music',
    'Nanotechnology',
    'Newspapers',
    'Nonprofit Organization Management',
    'Oil & Energy',
    'Online Publishing',
    'Outsourcing/Offshoring',
    'Package/Freight Delivery',
    'Packaging & Containers',
    'Paper & Forest Products',
    'Performing Arts',
    'Pharmaceuticals',
    'Philanthropy',
    'Photography',
    'Plastics',
    'Political Organization',
    'Primary/Secondary',
    'Printing',
    'Professional Training',
    'Program Development',
    'Public Policy',
    'Public Relations',
    'Public Safety',
    'Publishing',
    'Railroad Manufacture',
    'Ranching',
    'Real Estate',
    'Recreational',
    'Facilities & Services',
    'Religious Institutions',
    'Renewables & Environment',
    'Research',
    'Restaurants',
    'Retail',
    'Security & Investigations',
    'Semiconductors',
    'Shipbuilding',
    'Sporting Goods',
    'Sports',
    'Staffing & Recruiting',
    'Supermarkets',
    'Telecommunications',
    'Textiles',
    'Think Tanks',
    'Tobacco',
    'Translation & Localization',
    'Transportation/Trucking/Railroad',
    'Utilities',
    'Venture Capital',
    'Veterinary',
    'Warehousing',
    'Wholesale',
    'Wine & Spirits',
    'Wireless',
    'Writing & Editing',
]

def sanitize_name(name:str) -> str:
    """Turns 'Wine & Spirits into WINE_AND_SPIRITS"""
    sanitized = name.replace("&", "and")
    sanitized = ''.join(e for e in sanitized if e.isalnum() or e.isspace())
    sanitized = sanitized.replace(" ", "_").upper()
    return sanitized


# IndustryEnum:Enum = Enum("IndustryEnum", {sanitize_name(name): name for name in industries})

# for industry in IndustryEnum:
#     print(f"{industry.name} = '{industry.value}'")