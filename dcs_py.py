import socket
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad
import base64

key = b'1234567890123456'  # 16 bytes key

def encrypt(msg):
    cipher = AES.new(key, AES.MODE_CBC)
    ct_bytes = cipher.encrypt(pad(msg.encode(), AES.block_size))
    return base64.b64encode(cipher.iv + ct_bytes)

s = socket.socket()
s.connect(("127.0.0.1", 1234))

message = "TEMP=30"
encrypted = encrypt(message)

s.send(encrypted)
print("Sent Encrypted:", encrypted)

s.close()