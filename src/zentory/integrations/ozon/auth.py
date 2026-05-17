from dataclasses import dataclass


@dataclass(frozen=True)
class MarketplaceAuth:
    api_key_env_name: str
    mock_mode: bool = True
