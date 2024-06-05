from abc import ABC, abstractmethod

class DataFetcher(ABC):
    """Abstract base class to define the interface for data fetching."""
    
    @abstractmethod
    def fetch_alerts(self) -> dict:
        """
        Abstract method to fetch data from a data source.
        Must be implemented by subclasses.
        """
        pass