import re


class TireCodeRegex:

    tire_code = re.compile(r'\b(\d+)/(\d+)[A-Z]+(\d+)\s+(\d+)(?:/(\d+))?([A-Z])\b')
    tire_code_2 = re.compile(r'\b(\d+)([A-Z]?R[A-Z]?)(\d+)([A-Z]?)\s+(\d+)(?:/(\d+))?([A-Z]?)\b') # matches '185R14C 102/100Q'
    tire_code_3 = re.compile(r'\b(\d+)/(\d+)Z?R(\d+)([A-Z]{1,2})?\s+(\d+)(?:/(\d+))?([A-Z]?)\b') # matches '195/70R15C 104/102R', '275/65R18LT 123/120'
    tire_code_offroad = re.compile(r'\b(\d+)X(\d+(\.\d+)?)Z?R(\d+)([A-Z]{1,2})?\s+(\d+)([A-Z]?)\b') # matches '35X12.5R20 125R', '33X12.5R20LT 114Q'
    tire_code_reinf = re.compile(r'(\d+)/(\d+)Z?R(\d+)') # matches '275/35ZR20 REINF'. Literally 1 tire on Fastco has this format lol
