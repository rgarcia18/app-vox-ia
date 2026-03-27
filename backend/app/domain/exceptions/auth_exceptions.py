class InvalidCredentialsException(Exception):
    pass

class InvalidTokenException(Exception):
    pass

class TooManyAttemptsException(Exception):
    def __init__(self, retry_after: int):
        self.retry_after = retry_after
        super().__init__(f"Too many attempts. Retry after {retry_after}s")
