from dataclasses import dataclass, field
from typing import Optional
from webweaver.modules.project_modules.speed_fanatics.categorization.base_handler import BaseHandler


@dataclass
class SpecData:
    weight: Optional[float] = field(default=None)
    height: Optional[float] = field(default=None)
    width: Optional[float] = field(default=None)
    length: Optional[float] = field(default=None)


class SpecHandler(BaseHandler):
    """Determine the product specs to help us calculate shipping costs."""


    def _weight(self) -> float:
        ...

    def _height(self) -> float:
        ...

    def _width(self) -> float:
        ...

    def _length(self) -> float:
        ...