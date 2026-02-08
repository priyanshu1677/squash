"""Configuration management for PM Agentic AI Platform."""

import json
import os
from pathlib import Path
from typing import Any, Dict, Optional

from dotenv import load_dotenv

from .logger import get_logger

logger = get_logger(__name__)

# Load environment variables
load_dotenv()


def get_env(key: str, default: Optional[str] = None, required: bool = False) -> str:
    """
    Get environment variable value.

    Args:
        key: Environment variable key
        default: Default value if not found
        required: Whether the variable is required

    Returns:
        Environment variable value

    Raises:
        ValueError: If required variable is not set
    """
    value = os.getenv(key, default)

    if required and value is None:
        raise ValueError(f"Required environment variable {key} is not set")

    return value


def load_config(config_path: Optional[Path] = None) -> Dict[str, Any]:
    """
    Load configuration from JSON file.

    Args:
        config_path: Path to configuration file (default: config/mcp_servers.json)

    Returns:
        Configuration dictionary
    """
    if config_path is None:
        config_path = Path(__file__).parent.parent.parent / "config" / "mcp_servers.json"

    if not config_path.exists():
        logger.warning(f"Configuration file not found: {config_path}")
        return {}

    try:
        with open(config_path, 'r') as f:
            config = json.load(f)
        logger.info(f"Loaded configuration from {config_path}")
        return config
    except Exception as e:
        logger.error(f"Error loading configuration: {e}")
        return {}


class Config:
    """Application configuration."""

    def __init__(self):
        self.app_name = get_env("APP_NAME", "PM Agentic AI Platform")
        self.environment = get_env("ENVIRONMENT", "development")
        self.log_level = get_env("LOG_LEVEL", "INFO")

        # API Keys
        self.openai_api_key = get_env("OPENAI_API_KEY", required=True)

        # Web settings
        self.web_host = get_env("WEB_HOST", "0.0.0.0")
        self.web_port = int(get_env("WEB_PORT", "8000"))

        # Data directories
        self.upload_dir = Path(get_env("UPLOAD_DIR", "./data/uploads"))
        self.cache_dir = Path(get_env("CACHE_DIR", "./data/cache"))

        # MCP settings
        self.use_mock_mcp = get_env("USE_MOCK_MCP", "true").lower() == "true"

        # Mixpanel
        self.mixpanel_project_id = get_env("MIXPANEL_PROJECT_ID", "")
        self.mixpanel_api_secret = get_env("MIXPANEL_API_SECRET", "")
        self.mixpanel_eu = get_env("MIXPANEL_EU", "false").lower() == "true"

        # PostHog
        self.posthog_api_key = get_env("POSTHOG_API_KEY", "")
        self.posthog_project_id = get_env("POSTHOG_PROJECT_ID", "")
        self.posthog_host = get_env("POSTHOG_HOST", "https://app.posthog.com")

        # Jira
        self.jira_domain = get_env("JIRA_DOMAIN", "")  # yourcompany.atlassian.net
        self.jira_email = get_env("JIRA_EMAIL", "")
        self.jira_api_token = get_env("JIRA_API_TOKEN", "")
        self.jira_project_key = get_env("JIRA_PROJECT_KEY", "")

        # Confluence (often same Atlassian credentials as Jira)
        self.confluence_domain = get_env("CONFLUENCE_DOMAIN", "")
        self.confluence_email = get_env("CONFLUENCE_EMAIL", "")
        self.confluence_api_token = get_env("CONFLUENCE_API_TOKEN", "")
        self.confluence_space_key = get_env("CONFLUENCE_SPACE_KEY", "")

        # Salesforce
        self.salesforce_instance_url = get_env("SALESFORCE_INSTANCE_URL", "")
        self.salesforce_access_token = get_env("SALESFORCE_ACCESS_TOKEN", "")

        # Create directories if they don't exist
        self.upload_dir.mkdir(parents=True, exist_ok=True)
        self.cache_dir.mkdir(parents=True, exist_ok=True)

        logger.info(f"Configuration loaded: {self.app_name} ({self.environment})")


# Global config instance
config = Config()
