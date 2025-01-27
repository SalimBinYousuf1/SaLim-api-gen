import importlib
import os
from typing import List, Dict, Any, Callable


class PluginManager:
    def __init__(self):
        self.plugins: Dict[str, Callable] = {}

    def load_plugins(self, plugin_dir: str):
        """Load all plugins from the specified directory."""
        for filename in os.listdir(plugin_dir):
            if filename.endswith(".py") and not filename.startswith("__"):
                module_name = filename[:-3]
                module = importlib.import_module(f"plugins.{module_name}")
                if hasattr(module, "register_plugin"):
                    plugin_name = getattr(module, "PLUGIN_NAME", module_name)
                    self.plugins[plugin_name] = module.register_plugin

    def get_plugin(self, name: str) -> Callable:
        """Get a plugin by name."""
        return self.plugins.get(name)

    def list_plugins(self) -> List[str]:
        """List all available plugins."""
        return list(self.plugins.keys())

    def execute_plugin(self, name: str, *args, **kwargs) -> Any:
        """Execute a plugin by name."""
        plugin = self.get_plugin(name)
        if plugin:
            return plugin(*args, **kwargs)
        else:
            raise ValueError(f"Plugin '{name}' not found.")


plugin_manager = PluginManager()
