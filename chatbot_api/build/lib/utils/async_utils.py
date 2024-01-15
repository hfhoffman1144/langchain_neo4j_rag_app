import asyncio


def async_retry(max_retries: int = 3, delay: int = 1):
    def decorator(func):
        async def wrapper(*args, **kwargs):
            for attempt in range(1, max_retries + 1):
                try:
                    # Call the decorated asynchronous function
                    result = await func(*args, **kwargs)
                    return result  # If successful, return the result
                except Exception as e:
                    print(f"Attempt {attempt} failed: {str(e)}")
                    await asyncio.sleep(delay)  # Introduce a delay before retrying

            raise ValueError(f"Failed after {max_retries} attempts")

        return wrapper

    return decorator
