from abc import ABC, abstractmethod

class BaseIntegration(ABC):
    """
    Har naye enterprise integration ko yeh do kaam aane chahiye:
    1. Data lana (fetch_data)
    2. Action lena / Data bhejna (send_action)
    """
    
    @abstractmethod
    def fetch_data(self, **kwargs):
        pass

    @abstractmethod
    def send_action(self, **kwargs):
        pass