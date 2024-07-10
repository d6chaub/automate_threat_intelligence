""" Enums for the structured fields and subfields within the AlertDocument class. """
from enum import Enum

class AggregatorPlatform(str, Enum):
    "Multiple inheritance from Enum, and str so serializable."
    FEEDLY = "Feedly"

class SummarizationStatus(str, Enum):
    "Multiple inheritance from Enum, and str so serializable."
    NOT_STARTED = "Not Started"
    IN_PROGRESS = "In Progress"
    COMPLETED = "Completed"
    FAILED = "Failed"

class TaggingStatus(str, Enum):
    "Multiple inheritance from Enum, and str so serializable."
    NOT_TAGGED = "Not Tagged"
    PARTIALLY_TAGGED = "Partially Tagged"
    FULLY_TAGGED = "Fully Tagged"