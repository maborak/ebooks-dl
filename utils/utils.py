from importlib import import_module


def get_engine(engine: str = 'none') -> callable:
    try:
        module = import_module(f".{engine}", package='engines')
    except Exception as e:
        print("+-----------------------------------")
        print(f"| engine: '{engine}' does not exist")
        print(f"| error: {e}")
        print("+-----------------------------------")
        exit()
    else:
        return module
