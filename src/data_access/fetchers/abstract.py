from abc import ABC, abstractmethod

class DataFetcher(ABC):
    """
    Abstract base class to define the interface for data fetching.
    
    There will be multiple concrete implementations of this class,
    corresponding to the different data sources needing fetching. Each
    of these implementations should conform to the interface defined here
    for ease of interchangeability.
    """
    
    @abstractmethod
    def fetch_alerts(self) -> dict:
        """
        Abstract method to fetch data from a data source.
        Must be implemented by subclasses.
        """
        pass