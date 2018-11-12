class AtomException(Exception):
    """Base exception"""
    pass


class TokenExpiredError(AtomException):
    pass


class AtomTokenError(AtomException):
    """error during decoding token"""
    pass


class AtomBadRequestError(AtomException):
    """error during generating token"""
    pass


class AtomTokenRevokedError(AtomException):
    """error when token is revoked"""
    pass


class AtomNotFoundError(AtomException):
    pass


class AtomClientProjectNotMatchError(AtomException):
    """error when Client does not match project"""
    pass


class AtomVendorProjectNotMatchError(AtomException):
    """error when Vendor does not match project"""
    pass


class AtomInvalidFilenameError(AtomException):
    """error when upload filename is not valid"""


class AtomInvalidFileCountError(AtomException):
    """error when upload files count are not valid"""


class AtomMQTTConnectionError(AtomException):
    """error when MQTT protocol not correct"""
    pass


class AtomMQTTPublishError(AtomException):
    """error when MQTT publish failed"""
    pass


class AtomLibraryDuplicateError(AtomException):
    """error when create same device"""
    message = None

    def __init__(self, message):
        super(AtomLibraryDuplicateError, self).__init__()
        self.message = message


class AtomDeviceDuplicateError(AtomException):
    """error when create same device"""
    message = None

    def __init__(self, message):
        super(AtomDeviceDuplicateError, self).__init__()
        self.message = message


class AtomPatternDuplicateError(AtomException):
    """error when create same device"""
    message = None

    def __init__(self, message):
        super(AtomPatternDuplicateError, self).__init__()
        self.message = message


class AtomAddPatternFailedError(AtomException):
    """error when wrong pattern action was received"""
    message = None

    def __init__(self, message):
        super(AtomAddPatternFailedError, self).__init__()
        self.message = message


class AtomTwoWaySSLUnauthorizedError(AtomException):
    """error when request header not valid"""
    message = None

    def __init__(self, message):
        super(AtomTwoWaySSLUnauthorizedError, self).__init__()
        self.message = message


class AtomWouldBlockError(AtomException):
    """Add for MQTT"""
    pass
