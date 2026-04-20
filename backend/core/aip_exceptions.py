class AIPError(Exception):
    def __init__(
        self,
        http_status_code: int,
        message: str,
        details: list[dict] | None = None,
    ) -> None:
        super().__init__(message)
        self.http_status_code = http_status_code
        self.message = message
        self.details = list(details or [])


class InvalidArgumentError(AIPError):
    def __init__(self, message: str, details: list[dict] | None = None) -> None:
        super().__init__(http_status_code=400, message=message, details=details)
