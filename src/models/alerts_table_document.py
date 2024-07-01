

@dataclass
class Alert:
    """
    This class dictates the format of the main, central table, in which
    all metadata is contained and updated for each alert that it received.
    The data in the structure is constantly synced with the data processing
    queue through the lifetime of the pipeline, to ensure that the table
    acts as the single source of truth for the alert data.
    """
    pass