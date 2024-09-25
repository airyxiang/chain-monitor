from cryptography.fernet import Fernet, MultiFernet


class FernetEngine:
    """
    Wrapper around Fernet that handles string <-> byte conversion.
    Loosely based off of concept in sqlalchemy-utils
    For now, just supports string type
    """

    def __init__(self, key):
        self.fernet = Fernet(key)

    def encrypt(self, val) -> bytes:
        if isinstance(val, str):
            val = val.encode()
        encrypted_bytes = self.fernet.encrypt(val)
        return encrypted_bytes

    def decrypt(self, val) -> str:
        decrypted_bytes = self.fernet.decrypt(val)
        decrypted_string = decrypted_bytes.decode('utf-8')
        return decrypted_string


class MultiFernetEngine(FernetEngine):
    def __init__(self, keys):
        fernets = [Fernet(key) for key in keys]
        self.fernet = MultiFernet(fernets)
        self.sub_fernets = fernets

    def rotate(self, token):
        return self.fernet.rotate(token)
