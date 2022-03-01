# micropython-cryptocfb
[![PayPal Donate][paypal_img]][paypal_link]
[![PyPI version][pypi_img]][pypi_link]
[![Downloads][downloads_img]][downloads_link]

  [paypal_img]: https://github.com/jacklinquan/images/blob/master/paypal_donate_badge.svg
  [paypal_link]: https://www.paypal.me/jacklinquan
  [pypi_img]: https://badge.fury.io/py/micropython-cryptocfb.svg
  [pypi_link]: https://badge.fury.io/py/micropython-cryptocfb
  [downloads_img]: https://pepy.tech/badge/micropython-cryptocfb
  [downloads_link]: https://pepy.tech/project/micropython-cryptocfb

A Python module to encrypt and decrypt data with AES-128 CFB mode.

This module works under MicroPython and it is tested with MicroPython V1.18.

For a compatible CPython version, please find [Python package cryptocfb](https://github.com/jacklinquan/cryptocfb).

## Installation
``` Python
>>> import upip
>>> upip.install('micropython-cryptocfb')
```
Alternatively just copy cryptocfb.py to the MicroPython device.

## Usage
``` python
>>> from cryptocfb import CryptoCFB
>>>
>>> key = b'0123456789abcdef'
>>> iv = bytes(reversed(key))
>>> cfb = CryptoCFB(key, iv)
>>>
>>> plain = b'This is a long message that needs to be encrypted.'
>>> cipher = cfb.encrypt(plain)
>>> cipher
bytearray(b"_#\xbf\x02\xd6\x19\x0c)\xd9\x18\xaf\xb9\xa4{JP\xf6j\xa3\xb2\xb2\xc6b\x9f\xae\x82\xa5\xd4\xaeen\xde\x12\x16\xfb\xf6\x079\x83\xd2\xbdC\'\x93\x9e\xc3\xeb\xc7\x03\x82")
>>> len(plain)
50
>>> len(cipher)
50
>>> cfb.reset_vector()
>>>
>>> cfb.decrypt(cipher)
bytearray(b'This is a long message that needs to be encrypted.')
>>> cfb.reset_vector()
>>>
>>> ba = bytearray(plain)
>>> ba1 = ba[0:16]
>>> ba2 = ba[16:32]
>>> ba3 = ba[32:48]
>>> ba4 = ba[48:64]
>>> cfb.crypt_inplace(ba1)
bytearray(b'_#\xbf\x02\xd6\x19\x0c)\xd9\x18\xaf\xb9\xa4{JP')
>>> cfb.crypt_inplace(ba2)
bytearray(b'\xf6j\xa3\xb2\xb2\xc6b\x9f\xae\x82\xa5\xd4\xaeen\xde')
>>> cfb.crypt_inplace(ba3)
bytearray(b"\x12\x16\xfb\xf6\x079\x83\xd2\xbdC\'\x93\x9e\xc3\xeb\xc7")
>>> cfb.crypt_inplace(ba4)
bytearray(b'\x03\x82')
>>> cfb.reset_vector()
>>>
>>> cfb.crypt_inplace(ba1, False)
bytearray(b'This is a long m')
>>> cfb.crypt_inplace(ba2, False)
bytearray(b'essage that need')
>>> cfb.crypt_inplace(ba3, False)
bytearray(b's to be encrypte')
>>> cfb.crypt_inplace(ba4, False)
bytearray(b'd.')
>>> cfb.reset_vector()
>>>
>>> ba
bytearray(b'This is a long message that needs to be encrypted.')
>>> cfb.crypt_inplace(ba)
bytearray(b"_#\xbf\x02\xd6\x19\x0c)\xd9\x18\xaf\xb9\xa4{JP\xf6j\xa3\xb2\xb2\xc6b\x9f\xae\x82\xa5\xd4\xaeen\xde\x12\x16\xfb\xf6\x079\x83\xd2\xbdC\'\x93\x9e\xc3\xeb\xc7\x03\x82")
>>> len(ba)
50
>>> ba.extend(bytearray(14))
>>> ba
bytearray(b"_#\xbf\x02\xd6\x19\x0c)\xd9\x18\xaf\xb9\xa4{JP\xf6j\xa3\xb2\xb2\xc6b\x9f\xae\x82\xa5\xd4\xaeen\xde\x12\x16\xfb\xf6\x079\x83\xd2\xbdC\'\x93\x9e\xc3\xeb\xc7\x03\x82\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00")
>>> cfb.reset_vector()
>>>
>>> cfb.crypt_inplace(ba, False)
bytearray(b'This is a long message that needs to be encrypted.d\xd5\x99vk\x08\x1c\x82\xf0_\xb8\x8aw\x85')
>>> cfb.reset_vector()
```

## AES-128 8-bit CFB mode
The 8-bit CFB mode is less efficient than the default (128-bit) CFB mode.
But its advantage is it can encrypt or decrypt data byte by byte.
So it is easy to implement data stream encryption or decryption with it.

``` python
>>> from cryptocfb import CryptoCFB
>>>
>>> key = b'0123456789abcdef'
>>> iv = bytes(reversed(key))
>>> cfb1 = CryptoCFB(key, iv, 8)
>>> cfb2 = CryptoCFB(key, iv, 8)
>>>
>>> plain = b'This is a long message that needs to be encrypted.'
>>> cipher = bytearray()
>>> decrypted_plain = bytearray()
>>>
>>> for i in range(len(plain)):
...     cb = cfb1.encrypt(plain[i : i + 1])
...     cipher.extend(cb)
...     db = cfb2.decrypt(cb)
...     decrypted_plain.extend(db)
...
>>> cipher
bytearray(b'_\xf7+\xf1`4\x88\x88\x88\xba\xfb\x87\xe0_Lc\xbf\xc9AM\x95\xf3\x8dR\x1b>~\x91\x00\x9a\x1f\t\x99$\x02\xfbC\x810_J\x89\x9a\x81>Z\xe6\x9f^H')
>>> decrypted_plain
bytearray(b'This is a long message that needs to be encrypted.')
```

During transmission, if any encrypted data byte is corrupted, the result decrypted data will be corrupted as well.
By the nature of CFB mode, the communication will recover by it self after several garbage bytes (17 bytes in the case below).
This self-recovery behaviour makes it suitable for serial communication where data corruption could happen.

``` python
>>> from cryptocfb import CryptoCFB
>>>
>>> key = b'0123456789abcdef'
>>> iv = bytes(reversed(key))
>>> cfb1 = CryptoCFB(key, iv, 8)
>>> cfb2 = CryptoCFB(key, iv, 8)
>>>
>>> plain = b'This is a long message that needs to be encrypted.'
>>> cipher = bytearray()
>>> decrypted_plain = bytearray()
>>>
>>> for i in range(len(plain)):
...     cb = cfb1.encrypt(plain[i : i + 1])
...     if i == 10:
...         cb[0] ^= 0x01
...     cipher.extend(cb)
...     db = cfb2.decrypt(cb)
...     decrypted_plain.extend(db)
...
>>> cipher
bytearray(b'_\xf7+\xf1`4\x88\x88\x88\xba\xfa\x87\xe0_Lc\xbf\xc9AM\x95\xf3\x8dR\x1b>~\x91\x00\x9a\x1f\t\x99$\x02\xfbC\x810_J\x89\x9a\x81>Z\xe6\x9f^H')
>>> decrypted_plain
bytearray(b'This is a m\x12\xa2;\xf5\xdb\xbd\x10\xa0\xc2\xbd\xa2\xa4\x05V\xc2\xdd needs to be encrypted.')
```
