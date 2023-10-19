class ValidationException(Exception):
    """ Webservice responded with a validation error """

    def __init__(self, message):
        self.message = message
        super().__init__(self.message)


class ServiceException(Exception):
    """ Webservice general exception error """

    def __init__(self, message):
        self.message = message
        super().__init__(self.message)


class NotAllowedException(Exception):
    """ Webservice not allowed exception error """

    def __init__(self, message):
        self.message = message
        super().__init__(self.message)
