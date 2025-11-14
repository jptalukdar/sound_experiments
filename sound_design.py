import os
import importlib
import inspect
from instruments.base_instrument import BaseInstrument

class InstrumentFactory:
    """
    Loads, caches, and creates instrument plugin instances.
    """
    
    def __init__(self):
        self.loaded_plugins = {}
        self._load_plugins()

    def _load_plugins(self, plugin_dir="instruments"):
        """
        Dynamically imports all instrument plugins from the plugin directory.
        """
        print(f"Loading instrument plugins from '{plugin_dir}'...")
        if not os.path.isdir(plugin_dir):
            print(f"Warning: Plugin directory '{plugin_dir}' not found.")
            return

        for filename in os.listdir(plugin_dir):
            if not filename.endswith(".py") or filename.startswith("__"):
                continue
                
            module_name = filename[:-3]
            module_path = f"{plugin_dir}.{module_name}"
            
            try:
                # Import the module (e.g., "instruments.basic_synths")
                module = importlib.import_module(module_path)
                
                # Find all classes in the module
                for name, obj in inspect.getmembers(module, inspect.isclass):
                    # Check if it's a valid plugin:
                    # 1. Is it a subclass of BaseInstrument?
                    # 2. Is it NOT BaseInstrument itself?
                    # 3. Is it defined in this module (not imported)?
                    if (issubclass(obj, BaseInstrument) and 
                        obj is not BaseInstrument and
                        obj.__module__ == module_path):
                        
                        plugin_name = name.lower()
                        if plugin_name in self.loaded_plugins:
                            print(f"Warning: Duplicate plugin name '{plugin_name}'.")
                        else:
                            self.loaded_plugins[plugin_name] = obj
                            print(f"  > Loaded: '{plugin_name}'")
                            
            except ImportError as e:
                print(f"Error loading plugin {module_path}: {e}")
        
        print(f"Total plugins loaded: {len(self.loaded_plugins)}")

    def create_instrument(self, name: str, **adsr_params):
        """
        Creates an instance of a loaded instrument.
        
        Args:
            name (str): The name of the instrument (e.g., "piano", "sine").
            **adsr_params: Envelope parameters (attack_s, decay_s, etc.)
            
        Returns:
            An instance of a BaseInstrument subclass.
            
        Raises:
            ValueError: If the instrument name is not found.
        """
        instrument_class = self.loaded_plugins.get(name.lower())
        
        if instrument_class:
            return instrument_class(**adsr_params)
        else:
            raise ValueError(
                f"Unknown instrument: '{name}'. "
                f"Available instruments: {list(self.loaded_plugins.keys())}"
            )