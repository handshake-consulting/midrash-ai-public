"""Special Errors"""
class NoPromptException(Exception):
    """Exception raised when prompt input is required, but not found in yaml."""

    def __init__(self, message:str="Input prompt not found in yaml."):
        super().__init__(message)

class StoreOrKeyException(Exception):
    """Exception raised when Yaml key error is found, something is wrong with your yaml"""

    def __init__(self, message:str="store or key not found in keywords."):
        super().__init__(message)
