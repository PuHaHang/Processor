from abc import ABC

from ..processor import Processor
from ..processor_type import ProcessorType


class RefinerStrategy (Processor, ABC):
    processor_type: ProcessorType = ProcessorType.REFINER
