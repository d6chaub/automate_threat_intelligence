from dataclasses import dataclass


# ToDo: Find the name of a 'row' in a non-relational table (document?) and re-name class appropriately.
#     Similarly for 'table'.
@dataclass
class TriageStagingRow:
    """
    TriageStagingRow is a data class that holds formatted data with enhancements such as 
    summarization and tagging. This data is stored in the TriageStaging table.
    This data is served to the frontend of the application, 
    where the user can make an informed decision about whether to process or discard 
    the row of data.
    """
    pass
