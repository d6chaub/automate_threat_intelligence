from abc import ABC, abstractmethod


class AlertsDAO(ABC):
    """
    Abstract base class for Alerts DAO to ensure each specific DAO implements these methods.
    """
    
    @abstractmethod
    def add_alert_if_not_exists(self, alert: dict):
        pass

    @abstractmethod
    def add_alerts_if_not_exist(self, alerts: list[dict]) -> list[int]:
        pass

    @abstractmethod
    def get_all_alerts(self):
        pass
