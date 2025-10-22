from importlib import import_module

__all__ = ["router"]

def __getattr__(name):
    if name == "router":
        # Import only when someone accesses app.agents.router
        return import_module(".router", __name__).router
    raise AttributeError(name)
