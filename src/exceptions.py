class CustomizeException(Exception):
    def __init__(self, message: str=None) -> None:
        self.message = message
        super().__init__(self.message)
        
    def __str__(self) -> str:
        return f'{self.message}'