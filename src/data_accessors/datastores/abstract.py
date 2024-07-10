from abc import ABC, abstractmethod
from models.alerts_table_document import AlertDocument

class AlertsDAO(ABC):
    """
    Abstract base class for Alerts DAO for a specific database DAO implementation.
    """
    
    @abstractmethod
    def add_alert_if_not_duplicate(self, alert: AlertDocument):
        pass



class TriageStagingDAO(ABC):
    """
    Abstract base class for TriageStaging DAO for a specific database DAO implementation.
    """
    
    @abstractmethod
    def add_staging_entity_if_not_exists(self, triage_staging: dict):
        pass

    @abstractmethod
    def add_staging_entities_if_not_exist(self, triage_stagings: list[dict]) -> list[int]:
        pass

    @abstractmethod
    def get_all_staging_entities(self):
        pass