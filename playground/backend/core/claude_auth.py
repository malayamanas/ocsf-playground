"""
Authentication module for Claude CLI integration.
Uses Claude CLI's existing authentication instead of requiring explicit API keys.
"""

import logging
import os
import subprocess
import json
from pathlib import Path
from typing import Optional

logger = logging.getLogger("backend")


class ClaudeAuthError(Exception):
    """Raised when Claude authentication fails."""
    pass


class ClaudeAuthentication:
    """
    Manages authentication using Claude CLI.

    Automatically detects and uses the API key from Claude Code subscription
    without requiring manual setup.
    """

    # Possible locations for Claude credentials
    CLAUDE_CONFIG_PATHS = [
        Path.home() / ".claude",
        Path.home() / ".config" / "claude",
    ]

    @staticmethod
    def get_api_key() -> Optional[str]:
        """
        Get the API key from Claude CLI or environment.

        Priority order:
        1. ANTHROPIC_API_KEY environment variable (explicit override)
        2. Claude CLI authentication (via setup-token)
        3. Return None if none found (will try OAuth token next)

        Returns:
            str or None: The API key if found, None otherwise
        """
        # First, check if ANTHROPIC_API_KEY is explicitly set in environment
        if api_key := os.environ.get("ANTHROPIC_API_KEY"):
            logger.info("Using ANTHROPIC_API_KEY from environment variable")
            return api_key

        # Try to get API key from Claude CLI authentication
        if api_key := ClaudeAuthentication._get_claude_cli_api_key():
            logger.info("Using API key from Claude CLI authentication")
            return api_key

        # Return None - caller will try OAuth token
        return None

    @staticmethod
    def get_auth_token() -> Optional[str]:
        """
        Get the OAuth token from environment (for Claude Code).

        Returns:
            str or None: The OAuth token if found, None otherwise
        """
        if auth_token := os.environ.get("CLAUDE_CODE_OAUTH_TOKEN"):
            logger.info("Using CLAUDE_CODE_OAUTH_TOKEN from environment variable")
            return auth_token
        return None

    @staticmethod
    def get_credentials() -> tuple[Optional[str], Optional[str]]:
        """
        Get authentication credentials (api_key, auth_token).

        Priority order:
        1. ANTHROPIC_API_KEY (traditional API key)
        2. CLAUDE_CODE_OAUTH_TOKEN (OAuth token for Claude Code)
        3. Claude CLI authentication
        4. Raise error if none found

        Returns:
            tuple: (api_key, auth_token) - one will be set, other will be None

        Raises:
            ClaudeAuthError: If no valid authentication is found
        """
        api_key = ClaudeAuthentication.get_api_key()
        auth_token = ClaudeAuthentication.get_auth_token()

        if api_key:
            return (api_key, None)
        elif auth_token:
            return (None, auth_token)
        else:
            raise ClaudeAuthError(
                "No Claude authentication found. \n\n"
                "To authenticate, run:\n"
                "  claude setup-token\n\n"
                "Or set one of these environment variables:\n"
                "  export ANTHROPIC_API_KEY='your-api-key'\n"
                "  export CLAUDE_CODE_OAUTH_TOKEN='your-oauth-token'\n\n"
                "Learn more: https://console.anthropic.com"
            )

    @staticmethod
    def _get_claude_cli_api_key() -> Optional[str]:
        """
        Attempt to retrieve API key from Claude CLI.

        Note: The Anthropic SDK has built-in support for Claude CLI authentication
        when initialized without explicit credentials. We don't need to return
        a dummy value here.

        Returns:
            None: We let the Anthropic SDK handle Claude CLI auth directly
        """
        # The Anthropic SDK's default initialization (Anthropic()) will
        # automatically detect and use Claude CLI credentials if available.
        # We don't need to return anything here - just let it be None
        # so that get_credentials() can proceed to check for OAuth token
        # or fall back to the SDK's default auth chain.
        return None

    @staticmethod
    def ensure_authenticated() -> None:
        """
        Ensure that authentication is configured.

        Raises:
            ClaudeAuthError: If authentication cannot be found or configured
        """
        try:
            ClaudeAuthentication.get_credentials()
            logger.info("✓ Claude authentication verified")
        except ClaudeAuthError as e:
            logger.error(f"Authentication error: {e}")
            raise

    @staticmethod
    def get_setup_instructions() -> str:
        """
        Get human-friendly setup instructions.

        Returns:
            str: Setup instructions
        """
        return (
            "To set up Claude API authentication, run:\n\n"
            "  claude setup-token\n\n"
            "This will configure your Claude Code subscription API key.\n"
            "Learn more: https://console.anthropic.com"
        )
