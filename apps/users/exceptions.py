class ServiceError(Exception):
    """
    Базовое исключение для сервисов.
    Используется для передачи сообщений об ошибках из сервисного слоя.
    """

    def __init__(self, message: str) -> None:
        """
        Инициализирует исключение с сообщением.

        :param message: Сообщение об ошибке
        """

        super().__init__(message)
        self.message = message

    def __str__(self):
        return self.message
