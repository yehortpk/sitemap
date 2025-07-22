class URLFormattingException(Exception):
    def __init__(self, message="URL format was violated"):
        super().__init__(message)