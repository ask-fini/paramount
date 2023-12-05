def record(func):
    def wrapper(*args, **kwargs):
        result = func(*args, **kwargs)
        print(f"args kwargs: {args}, {kwargs}, result: {result}")
        return result
    return wrapper