# from hashlib import sha256
# import base64
# from Crypto import Random
# from Crypto.Cipher import AES
#
# BS = 16
# pad = lambda s: bytes(s + (BS - len(s) % BS) * chr(BS - len(s) % BS), 'utf-8')
# unpad = lambda s: s[0:-ord(s[-1:])]
#
#
# class AESCipher:
#
#     def __init__(self, key):
#         self.key = bytes(key, 'utf-8')
#
#     def encrypt(self, raw):
#         raw = pad(raw)
#         iv = Random.new().read(AES.block_size)
#         cipher = AES.new(self.key, AES.MODE_CBC, iv)
#         return base64.b64encode(iv + cipher.encrypt(raw))
#
#     def decrypt(self, enc):
#         enc = base64.b64decode(enc)
#         iv = enc[:16]
#         cipher = AES.new(self.key, AES.MODE_CBC, iv)
#         return unpad(cipher.decrypt(enc[16:])).decode('utf8')
#
#
# cipher = AESCipher('mysecretpassword')
# encrypted = cipher.encrypt('Secret')
# decrypted = cipher.decrypt(encrypted)
#
# print(encrypted)
# print(decrypted)
import base64
import hashlib
from Crypto import Random
from Crypto.Cipher import AES


class AESCipher(object):

    def __init__(self, key, iv):
        self.bs = 32
        self.key = hashlib.sha256(key.encode()).digest()
        self.iv = iv

    def encrypt(self, raw):
        raw = self._pad(raw)
        # iv = Random.new().read(AES.block_size)
        cipher = AES.new(self.key, AES.MODE_CFB, self.iv, segment_size=128)
        return base64.b64encode(self.iv + cipher.encrypt(raw))

    def decrypt(self, enc):
        enc = base64.b64decode(enc)
        # iv = enc[:AES.block_size]
        cipher = AES.new(self.key, AES.MODE_CFB, self.iv, segment_size=128)
        return self._unpad(cipher.decrypt(enc[AES.block_size:])).decode('utf-8')

    def _pad(self, s):
        return bytes(s + (self.bs - len(s) % self.bs) * chr(self.bs - len(s) % self.bs), 'utf-8')

    @staticmethod
    def _unpad(s):
        return s[0:-ord(s[-1:])]


cipher = AESCipher('mysecretpassword', b'1234567890123456')
encrypted = cipher.encrypt('Secret')
decrypted = cipher.decrypt('YbQ3LCM=')
print(encrypted)
z = encrypted.decode("utf-8")
print(z)
print(z.encode('utf-8'))
print(decrypted)
