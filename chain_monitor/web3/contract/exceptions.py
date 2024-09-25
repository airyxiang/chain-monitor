class Web3Error(BaseException):
    pass


class PrivateKeyNotFoundError(BaseException):
    pass


class CheckSumAddressError(Web3Error):
    pass


class TransactionSigningError(Web3Error):
    pass


class TransactionSendingError(Web3Error):
    pass


class NonceError(TransactionSendingError):
    pass


class TransactionNotMinedError(TransactionSendingError):
    pass
