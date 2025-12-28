"""
Configuration Manager for Roblox Account Manager CLI
Handles all customizable settings with full flexibility
"""

import os
import json
from typing import Any, Dict, Optional

DEFAULT_CONFIG = {
    # Browser settings
    "browser": {
        "headless": False,
        "window_size": {"width": 800, "height": 600},
        "user_agent": "",
        "disable_images": True,
        "disable_javascript": False,
        "timeout": 30
    },
    
    # Account operations
    "account": {
        "default_website": "https://www.roblox.com/login",
        "login_timeout": 300,
        "add_amount": 1,
        "validate_on_add": True,
        "custom_javascript": ""
    },
    
    # Launch settings
    "launch": {
        "default_launcher": "default",  # default, bloxstrap, fishstrap
        "default_game_id": "",
        "default_private_server": "",
        "auto_launch_delay": 0
    },
    
    # detection script
    # uh rn url only works lol
    # i vibe-coded cookie and api (i regret the decision)
    "detection": {
        "method": "url",  # url, cookie, api
        "custom_script": "",
        "success_indicators": [
            "roblox.com/home",
            "roblox.com/discover",
            "roblox.com/charts"
        ],
        "failure_indicators": [
            "roblox.com/login",
            "roblox.com/newlogin"
        ],
        "poll_interval": 0.5
    },
    
    # CLI appearance
    "appearance": {
        "theme": "default",  # default, minimal, hacker, custom
        "colors": {
            "primary": "cyan",
            "secondary": "white",
            "success": "green",
            "error": "red",
            "warning": "yellow",
            "info": "blue",
            "prompt": "magenta"
        },
        "show_banner": True,
        "show_loading": True,
        "loading_style": "dots",  # dots, spinner, bar, custom
        "custom_banner": "",
        "prompt_symbol": "❯",
        "show_timestamps": False
    },
    
    # Output settings
    "output": {
        "verbosity": "normal",  # quiet, normal, verbose, debug
        "format": "pretty",  # pretty, json, minimal
        "show_errors": True,
        "log_to_file": False,
        "log_file": "ram_cli.log"
    },
    
    # Command aliases
    "aliases": {
        "l": "list",
        "a": "add",
        "d": "delete",
        "v": "validate",
        "i": "info",
        "la": "launch",
        "h": "home",
        "c": "config",
        "q": "quit",
        "?": "help"
    },
    
    # Scripts/automation
    "scripts": {
        "on_startup": [],
        "on_account_add": [],
        "on_account_delete": [],
        "on_launch": [],
        "custom_scripts": {}
    }
}


class ConfigManager:
    """Manages all CLI configuration with full customizability"""
    
    def __init__(self, config_path: str = None):
        if config_path is None:
            self.config_path = os.path.join("AccountManagerData", "cli_config.json")
        else:
            self.config_path = config_path
        
        self.config = self._load_config()
    
    def _load_config(self) -> Dict:
        """Load configuration from file or create default"""
        if os.path.exists(self.config_path):
            try:
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    loaded = json.load(f)
                # Merge with defaults to ensure all keys exist
                return self._deep_merge(DEFAULT_CONFIG.copy(), loaded)
            except (json.JSONDecodeError, IOError):
                return DEFAULT_CONFIG.copy()
        return DEFAULT_CONFIG.copy()
    
    def _deep_merge(self, base: Dict, override: Dict) -> Dict:
        """Deep merge two dictionaries"""
        result = base.copy()
        for key, value in override.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = self._deep_merge(result[key], value)
            else:
                result[key] = value
        return result
    
    def save(self) -> bool:
        """Save configuration to file"""
        try:
            os.makedirs(os.path.dirname(self.config_path), exist_ok=True)
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=2)
            return True
        except IOError:
            return False
    
    def get(self, key_path: str, default: Any = None) -> Any:
        """
        Get a configuration value using dot notation
        Example: config.get("browser.headless") -> False
        """
        keys = key_path.split('.')
        value = self.config
        try:
            for key in keys:
                value = value[key]
            return value
        except (KeyError, TypeError):
            return default
    
    def set(self, key_path: str, value: Any) -> bool:
        """
        Set a configuration value using dot notation
        Example: config.set("browser.headless", True)
        """
        keys = key_path.split('.')
        target = self.config
        try:
            for key in keys[:-1]:
                if key not in target:
                    target[key] = {}
                target = target[key]
            
            # Type conversion based on existing value
            if keys[-1] in target:
                existing = target[keys[-1]]
                if isinstance(existing, bool):
                    if isinstance(value, str):
                        value = value.lower() in ('true', '1', 'yes', 'on')
                elif isinstance(existing, int) and not isinstance(existing, bool):
                    value = int(value)
                elif isinstance(existing, float):
                    value = float(value)
            
            target[keys[-1]] = value
            return self.save()
        except (KeyError, TypeError, ValueError):
            return False
    
    def reset(self, key_path: str = None) -> bool:
        """Reset configuration to defaults (all or specific key)"""
        if key_path is None:
            self.config = DEFAULT_CONFIG.copy()
        else:
            keys = key_path.split('.')
            default_value = DEFAULT_CONFIG
            try:
                for key in keys:
                    default_value = default_value[key]
                self.set(key_path, default_value)
            except (KeyError, TypeError):
                return False
        return self.save()
    
    def list_all(self, prefix: str = "") -> Dict[str, Any]:
        """Get all configuration as flat dictionary"""
        result = {}
        
        def flatten(obj, path=""):
            if isinstance(obj, dict):
                for k, v in obj.items():
                    new_path = f"{path}.{k}" if path else k
                    if prefix and not new_path.startswith(prefix):
                        if not prefix.startswith(new_path):
                            continue
                    flatten(v, new_path)
            else:
                if not prefix or path.startswith(prefix):
                    result[path] = obj
        
        flatten(self.config)
        return result
    
    def export_config(self, filepath: str) -> bool:
        """Export configuration to a file"""
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=2)
            return True
        except IOError:
            return False
    
    def import_config(self, filepath: str) -> bool:
        """Import configuration from a file"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                imported = json.load(f)
            self.config = self._deep_merge(DEFAULT_CONFIG.copy(), imported)
            return self.save()
        except (json.JSONDecodeError, IOError):
            return False
    
    def add_alias(self, alias: str, command: str) -> bool:
        """Add a command alias"""
        self.config["aliases"][alias] = command
        return self.save()
    
    def remove_alias(self, alias: str) -> bool:
        """Remove a command alias"""
        if alias in self.config["aliases"]:
            del self.config["aliases"][alias]
            return self.save()
        return False
    
    def get_alias(self, alias: str) -> Optional[str]:
        """Get command for an alias"""
        return self.config["aliases"].get(alias)
    
    def add_custom_script(self, name: str, commands: list) -> bool:
        """Add a custom automation script"""
        self.config["scripts"]["custom_scripts"][name] = commands
        return self.save()
    
    def get_custom_script(self, name: str) -> Optional[list]:
        """Get a custom script by name"""
        return self.config["scripts"]["custom_scripts"].get(name)
