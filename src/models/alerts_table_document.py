from dataclasses import dataclass
from .enums import SummarizationStatus, TaggingStatus, AggregatorPlatform


""" Classes for the structured fields and subfields within the AlertDocument class. """
@dataclass
class SummarizationInfo:
    """
    SummarizationInfo holds the summarization details of an alert, including
    the summarization status and the summary text if available.
    
    Attributes:
        status: The current status of the summarization process as an enumeration.
        summary_text: The summarized text of the alert, if available.
    """
    status: SummarizationStatus
    summary_text: str | None = None

@dataclass
class TagsInfo:
    """
    TagsInfo holds the tagging details of an alert, including
    the current status of the tagging process and a list of associated tags.
    
    Attributes:
        status: The current status of the tagging process as an enumeration.
        tags: A list of tags associated with the alert.
    """
    status: TaggingStatus
    tags: list[str] | None = None


# The main AlertDocument class that will hold the data and above typed fields.
@dataclass
class AlertDocument:
    """
    AlertDocument defines the schema for storing all metadata related to an alert.
    This structure serves as the single source of truth for alert data, continuously
    synchronized with the data processing pipeline.

    Attributes:
        id: A unique identifier for each alert.
        aggregatorPlatform: The platform or service where the data was aggregated.
        publicationSourceUrl: The URL of the original publication source.
        alertData: A dictionary containing the raw data of the alert from the aggregation platform.
        summaryData: An instance of SummarizationInfo containing summarization details.
        tagsData: A dictionary containing the tags associated with the alert.
    """
    id: str
    aggregatorPlatform: AggregatorPlatform
    publicationSourceUrl: str
    alertData: dict # Using Dict to store raw, unstructured data. # ToDo: Don't enforce a schema here. Just store the raw data.
    summaryData: SummarizationInfo
    tagsData: TagsInfo

# ToDo: Think this is a great use-case for subclassing.
# Make different fields etc for Feedly and other etc. Only if they actually have different needs in the end though.
