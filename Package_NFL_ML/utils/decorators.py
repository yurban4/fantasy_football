def step(func):
    def wrapper(*args, **kwargs):
        print(f"Running step: {func.__name__}")
        return func(*args, **kwargs)
    return wrapper
