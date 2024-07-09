""" Enums for the structured fields and subfields within the AlertDocument class. """
from enum import Enum

class AggregatorPlatform(Enum):
    FEEDLY = "Feedly"

class SummarizationStatus(Enum):
    NOT_STARTED = "Not Started"
    IN_PROGRESS = "In Progress"
    COMPLETED = "Completed"
    FAILED = "Failed"

class TaggingStatus(Enum):
    NOT_TAGGED = "Not Tagged"
    PARTIALLY_TAGGED = "Partially Tagged"
    FULLY_TAGGED = "Fully Tagged"