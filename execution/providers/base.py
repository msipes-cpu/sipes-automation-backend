from abc import ABC, abstractmethod
from typing import List, Dict

class EmailProvider(ABC):
    def __init__(self, api_key: str):
        self.api_key = api_key

    @abstractmethod
    def get_accounts(self) -> List[Dict]:
        """Return list of accounts with standardized keys: id, email, reputation/warmup_stats"""
        pass

    @abstractmethod
    def tag_account(self, account_id: str, tag_text: str):
        """Apply a tag to an account (create if missing)"""
        pass

    @abstractmethod
    def get_campaigns_for_account(self, account_id: str) -> List[str]:
        """Return list of Campaign IDs this account is active in"""
        pass

    @abstractmethod
    def add_account_to_campaign(self, campaign_id: str, account_id: str):
        pass

    @abstractmethod
    def remove_account_from_campaign(self, campaign_id: str, account_id: str):
        pass
