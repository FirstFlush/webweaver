from re import Pattern, Match
from typing import Callable
from .regex import TireCodeRegex


class TireCodeParsingError(Exception):
    """Raised when the tire code can not be successfully parsed."""
    pass


class TireSpecs:

    def __init__(self):
        self.SERVICE_TYPE = None
        self.TIRE_WIDTH = None
        self.ASPECT_RATIO = None
        self.WHEEL_DIAMETER = None
        self.OVERALL_DIAMETER = None
        self.LOAD_INDEX = None
        self.LOAD_INDEX_DUAL = None
        self.SPEED_RATING = None


class TireCodeParser:
    """
    Params:
        use_search - use re.Pattern.search() instead of re.Pattern.match()
        raise_exc - Raise an exception (or not) if no tire-code data is found by any of the regex patterns.
        *args/**kwargs - optional params you want passed to re.Pattern.match() / re.Pattern.search()
    """
    @property
    def specs_dict(self) -> dict:
        """If you prefer to have the specs as a dictionary instead of a different class."""
        d = {}
        for key, value in self.specs.__dict__.items():
            d[key] = value
        return d

    def __init__(
            self,
            tire_code: str,
            use_search: bool = False,
            raise_exc: bool = True,
            *args,
            **kwargs
    ):
        self._use_search = use_search
        self._raise_exc = raise_exc
        self.tire_code = self._preprocess(tire_code)
        self.regex = TireCodeRegex
        self.pattern_to_method = self._pattern_to_method_mapping()
        self.specs = TireSpecs()
        self._get_specs(*args, **kwargs)

    def _inch_to_mm(self, inches: float) -> float:
        """Converts inches to mm"""
        return inches * 25.4

    def _pattern_to_method_mapping(self) -> dict[Pattern, Callable]:
        """Not all tire codes contain the same information. Different regex patterns
        will match different sets of tire data. This mapping matches each regex pattern
        to it's method for populating tire specs with its particular set of data.
        """
        return {
            self.regex.tire_code: self._populate_from_tire_code,
            self.regex.tire_code_2: self._populate_from_tire_code_2,
            self.regex.tire_code_3: self._populate_from_tire_code_3,
            self.regex.tire_code_offroad: self._populate_from_tire_code_offroad,
            self.regex.tire_code_reinf: self._populate_from_tire_code_reinf,
        }

    def _preprocess(self, tire_code: str) -> str:
        if not isinstance(tire_code, str):
            raise ValueError(
                f"tire_code must be of type 'str', not '{type(tire_code).__name__}'")
        return tire_code.upper().strip().replace('(', '').replace(')', '')

    def _get_specs(self, *args, **kwargs):
        """Try each regex pattern until we get a match, then call that pattern's associated
        method to populate TireSpec with the tire data.
        """
        for pattern, method in self.pattern_to_method.items():
            if self._use_search:
                regex_match = pattern.search(self.tire_code, *args, **kwargs)
            else:
                regex_match = pattern.match(self.tire_code, *args, **kwargs)
            if regex_match:
                method(regex_match)
                return

        if self._raise_exc:
            raise TireCodeParsingError(
                f"Can't parse tire code: '{self.tire_code}'")

    def _populate_from_tire_code(self, match: Match):
        self.specs.SERVICE_TYPE = None
        self.specs.TIRE_WIDTH = match.group(1)
        self.specs.ASPECT_RATIO = match.group(2)
        self.specs.WHEEL_DIAMETER = match.group(3)
        self.specs.LOAD_INDEX = match.group(4)
        self.specs.LOAD_INDEX_DUAL = match.group(5)
        self.specs.SPEED_RATING = match.group(6)

    def _populate_from_tire_code_2(self, match: Match):
        self.specs.TIRE_WIDTH = match.group(1)
        self.specs.ASPECT_RATIO = None
        self.specs.WHEEL_DIAMETER = match.group(3)
        self.specs.SERVICE_TYPE = match.group(4)
        self.specs.LOAD_INDEX = match.group(5)
        self.specs.LOAD_INDEX_DUAL = match.group(6)
        self.specs.SPEED_RATING = match.group(7)

    def _populate_from_tire_code_3(self, match: Match):
        self.specs.TIRE_WIDTH = match.group(1)
        self.specs.ASPECT_RATIO = match.group(2)
        self.specs.WHEEL_DIAMETER = match.group(3)
        self.specs.SERVICE_TYPE = match.group(4)
        self.specs.LOAD_INDEX = match.group(5)
        self.specs.LOAD_INDEX_DUAL = match.group(6)
        self.specs.SPEED_RATING = match.group(7)

    def _populate_from_tire_code_offroad(self, match: Match):
        """tire width is converted from inch to mm if its value is less than 50"""
        width_inches = float(match.group(2))
        self.specs.OVERALL_DIAMETER = match.group(1)
        self.specs.ASPECT_RATIO = None
        self.specs.TIRE_WIDTH = str(self._inch_to_mm(
            width_inches)) if width_inches <= 50 else str(width_inches)
        self.specs.WHEEL_DIAMETER = match.group(4)
        self.specs.SERVICE_TYPE = match.group(5)
        self.specs.LOAD_INDEX = match.group(6)
        self.specs.SPEED_RATING = match.group(7)

    def _populate_from_tire_code_reinf(self, match: Match):
        self.specs.SERVICE_TYPE = None
        self.specs.TIRE_WIDTH = match.group(1)
        self.specs.ASPECT_RATIO = match.group(2)
        self.specs.WHEEL_DIAMETER = match.group(3)
        self.specs.LOAD_INDEX = None
        self.specs. SPEED_RATING = None
