from abc import ABC, abstractmethod
from typing import Any, Dict, Optional

class BaseTool(ABC):
    name: str
    description: str

    @abstractmethod
    async def run(self, *args, **kwargs) -> Any:
        pass
