from webweaver.webscraping.fuzzy_matching.fuzzy_handler import FuzzyHandler

brands = [
    'Pirelli', 'Bridgestone', 'BF GoodRich', 'Yokohama', 'Farroad', 'Falken', 'Continental', 'Toyo Tire',
]

fuzz = FuzzyHandler(brands, preprocess=True)

print(fuzz.best_match('Pirelli Tires'))