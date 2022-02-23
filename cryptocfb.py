# -*- coding: utf-8 -*-
"""A Python module to encrypt and decrypt data with AES-128 CFB mode.

Author: Quan Lin
License: MIT
"""

# Project version
__version__ = "0.1.0"
__all__ = ["CryptoCFB"]

s_box = b"c|w{\xf2ko\xc50\x01g+\xfe\xd7\xabv\xca\x82\xc9}\xfaYG\xf0\xad\xd4\xa2\xaf\x9c\xa4r\xc0\xb7\xfd\x93&6?\xf7\xcc4\xa5\xe5\xf1q\xd81\x15\x04\xc7#\xc3\x18\x96\x05\x9a\x07\x12\x80\xe2\xeb'\xb2u\t\x83,\x1a\x1bnZ\xa0R;\xd6\xb3)\xe3/\x84S\xd1\x00\xed \xfc\xb1[j\xcb\xbe9JLX\xcf\xd0\xef\xaa\xfbCM3\x85E\xf9\x02\x7fP<\x9f\xa8Q\xa3@\x8f\x92\x9d8\xf5\xbc\xb6\xda!\x10\xff\xf3\xd2\xcd\x0c\x13\xec_\x97D\x17\xc4\xa7~=d]\x19s`\x81O\xdc\"*\x90\x88F\xee\xb8\x14\xde^\x0b\xdb\xe02:\nI\x06$\\\xc2\xd3\xacb\x91\x95\xe4y\xe7\xc87m\x8d\xd5N\xa9lV\xf4\xeaez\xae\x08\xbax%.\x1c\xa6\xb4\xc6\xe8\xddt\x1fK\xbd\x8b\x8ap>\xb5fH\x03\xf6\x0ea5W\xb9\x86\xc1\x1d\x9e\xe1\xf8\x98\x11i\xd9\x8e\x94\x9b\x1e\x87\xe9\xceU(\xdf\x8c\xa1\x89\r\xbf\xe6BhA\x99-\x0f\xb0T\xbb\x16"
r_con = b"\x00\x01\x02\x04\x08\x10 @\x80\x1b6l\xd8\xabM\x9a/^\xbcc\xc6\x975j\xd4\xb3}\xfa\xef\xc5\x919"


def sub_bytes(s):
    for i in range(4):
        for j in range(4):
            s[i][j] = s_box[s[i][j]]
    return s


def shift_rows(s):
    s[0][1], s[1][1], s[2][1], s[3][1] = s[1][1], s[2][1], s[3][1], s[0][1]
    s[0][2], s[1][2], s[2][2], s[3][2] = s[2][2], s[3][2], s[0][2], s[1][2]
    s[0][3], s[1][3], s[2][3], s[3][3] = s[3][3], s[0][3], s[1][3], s[2][3]
    return s


def add_round_key(s, k):
    for i in range(4):
        for j in range(4):
            s[i][j] ^= k[i][j]
    return s


def xtime(b):
    return (((b << 1) ^ 0x1B) & 0xFF) if (b & 0x80) else (b << 1)


def mix_single_column(a):
    t = a[0] ^ a[1] ^ a[2] ^ a[3]
    u = a[0]
    a[0] ^= t ^ xtime(a[0] ^ a[1])
    a[1] ^= t ^ xtime(a[1] ^ a[2])
    a[2] ^= t ^ xtime(a[2] ^ a[3])
    a[3] ^= t ^ xtime(a[3] ^ u)


def mix_columns(s):
    for i in range(4):
        mix_single_column(s[i])
    return s


def bytes2matrix(text):
    return [list(text[i : i + 4]) for i in range(0, len(text), 4)]


def matrix2bytes(matrix):
    return bytes(sum(matrix, []))


def xor_bytes(a, b):
    return bytes(i ^ j for i, j in zip(a, b))


def expand_key128(key):
    key_columns = bytes2matrix(key)
    i = 1
    while len(key_columns) < 44:
        word = list(key_columns[-1])
        if len(key_columns) % 4 == 0:
            word.append(word.pop(0))
            word = [s_box[b] for b in word]
            word[0] ^= r_con[i]
            i += 1
        word = xor_bytes(word, key_columns[-4])
        key_columns.append(word)
    return [key_columns[4 * i : 4 * (i + 1)] for i in range(len(key_columns) // 4)]


class CryptoCFB:
    def __init__(self, key, iv):
        assert len(key) == 16 and len(iv) == 16
        self._key_matrices = expand_key128(key)
        self.next_vector = self._iv = iv

    def _encrypt_block(self, block):
        assert len(block) == 16
        block_state = add_round_key(bytes2matrix(block), self._key_matrices[0])
        for i in range(1, 10):
            add_round_key(
                mix_columns(shift_rows(sub_bytes(block_state))), self._key_matrices[i]
            )
        add_round_key(shift_rows(sub_bytes(block_state)), self._key_matrices[-1])
        return matrix2bytes(block_state)

    def reset_vector(self):
        # Reset next_vector before re-use.
        self.next_vector = self._iv

    def crypt_inplace(self, buf, is_encrypt=True):
        # If not the last part of the data, size of buf must be multiple of 16.
        for i in range(0, len(buf), 16):
            xor_input = buf[i : i + 16]
            xor_output = xor_bytes(xor_input, self._encrypt_block(self.next_vector))
            buf[i : i + 16] = xor_output
            self.next_vector = xor_output if is_encrypt else xor_input
        return buf

    def encrypt(self, plain):
        return self.crypt_inplace(bytearray(plain))

    def decrypt(self, cipher):
        return self.crypt_inplace(bytearray(cipher), False)
