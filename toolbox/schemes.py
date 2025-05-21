from typing import ClassVar

from pydantic import BaseModel

from toolbox.cipher import CipherSuiteManager


class BaseScheme(BaseModel):
    pass


class SensitiveDataScheme(BaseScheme):
    _sensitive_attributes: ClassVar[list[str]] = []
    _cipher_suite_manager: ClassVar[CipherSuiteManager] = None

    class Config:
        extra = "ignore"

    @property
    def cipher_suite_manager(self) -> CipherSuiteManager:
        if SensitiveDataScheme._cipher_suite_manager:
            return SensitiveDataScheme._cipher_suite_manager
        raise RuntimeError("cipher_suite_manager not set")

    @classmethod
    def set_cipher_suite_manager(cls, suite: CipherSuiteManager):
        cls._cipher_suite_manager = suite

    def encrypt_fields(self):
        fields = self._sensitive_attributes
        for field in fields:
            if hasattr(self, field):
                value = getattr(self, field)
                if value is not None:
                    encrypted_value = self._cipher_suite_manager.encrypt(value)
                    setattr(self, field, encrypted_value)
        return self

    def decrypt_fields(self):
        fields = self._sensitive_attributes
        for field in fields:
            if hasattr(self, field):
                value = getattr(self, field)
                if value is not None:
                    decrypted_value = self._cipher_suite_manager.decrypt(value)
                    setattr(self, field, decrypted_value)
        return self
