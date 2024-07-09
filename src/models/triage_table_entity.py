from dataclasses import dataclass

@dataclass
class TriageStagingEntity:
    """
    TriageStagingEntity represents an individual record in the 'TriageStaging' database
    (or collection, if non-relational). This entity holds data extracted and consolidated
    from various threat intelligence sources. Each entity includes details such as the
    platform of aggregation, source URL, content title, categories associated with the 
    threat, and the timestamp of data aggregation.

    These entities are utilized by the frontend of the Threat Intelligence Triage Portal,
    where users interact with the data to make decisions on further actions such as
    summarization, categorization, or submitting to Azure Devops as a work item.

    Attributes:
        id: An identifier unique to each entity.
        aggregatorPlatform: The platform or service where the data was aggregated.
        publicationSourceUrl: The URL of the original publication source.
        title: The title of the content or report.
        category: A list of categories or tags associated with the content.
        timestamp: The date and time when the content was published or aggregated.
    """
    id: str # Have a unique id but perform the update based ... # Take this from the other table I think (the main one...)
    publicationSourceUrl: str
    aggregatorPlatform: str
    title: str
    category: list
    timestamp: str
