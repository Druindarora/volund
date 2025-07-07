from dataclasses import dataclass, field
from typing import List


@dataclass
class ModuleInfo:
    name: str = ""
    version: str = "0.1.0"
    description: str = ""
    icon_path: str = ""
    tags: List[str] = field(default_factory=list)
    favorite: bool = False
    mobile: bool = False
    path: str = ""
