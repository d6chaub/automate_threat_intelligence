from dataclasses import dataclass

from pydantic import BaseModel, constr


# ToDo: Document the data fields as part of the docstring properly,
#    rather than inline.
@dataclass
class ProcessingQueueMessage:
    """
    ProcessingQueueItem represents the structure of the data that is sent from
    a given fetcher class to the processing queue, where it will have additional
    processing done on it. Note that the structure of the json 'alert' object
    from each fetcher will differ, and it is the responsibility of the fetcher
    to convert the data into this structure before sending it to the processing.
    """
    alert_text: constr(1) # This field should always contain text, from the ingestion pipeline.
    alert_summary: str # This field often starts off empty, at the beginning of the processing pipeline.
    alert_tags: dict # Begins pipeline as the empty dict.
    # Think about other fields that the user will want to see. Maybe ask as well in meeting.
    # Most of them will be the same for the 
