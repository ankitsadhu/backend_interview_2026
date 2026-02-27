"""
main.py — Host application demonstrating the plugin system.
"""
from core import PluginManager


def run_app():
    print("Initializing Plugin Manager...")
    manager = PluginManager()

    print("Discovering and loading plugins...")
    manager.discover_and_load()

    plugins = manager.active_plugins
    print(f"Loaded {len(plugins)} plugins: {[p.name for p in plugins]}")
    print("-" * 40)

    # Use the StringOpsPlugin
    try:
        string_plugin = manager.get_plugin("StringOpsPlugin")
        print(f"Executing {string_plugin.name} (v{string_plugin.version})")
        
        data = {"operation": "reverse", "text": "Dynamic Plugins in Python"}
        result = string_plugin.execute(data)
        print(f"  Input:  {data['text']}")
        print(f"  Result: {result}")
        print("-" * 40)
    except KeyError:
        print("StringOpsPlugin not found!")

    # Use the MathOpsPlugin
    try:
        math_plugin = manager.get_plugin("MathOpsPlugin")
        print(f"Executing {math_plugin.name} (v{math_plugin.version})")
        
        data = {"operation": "multiply", "a": 12.5, "b": 4}
        result = math_plugin.execute(data)
        print(f"  Input:  {data['a']} * {data['b']}")
        print(f"  Result: {result}")
        print("-" * 40)
    except KeyError:
        print("MathOpsPlugin not found!")


if __name__ == "__main__":
    run_app()
