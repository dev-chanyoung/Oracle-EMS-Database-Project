# security.py
# 민감정보 저장 규칙: 비밀번호는 단방향 해시, 주민등록번호는 AES-256-GCM 양방향 암호화
import base64
import os
import re

from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from werkzeug.security import generate_password_hash

RRN_PATTERN = re.compile(r'^\d{6}-\d{7}$')
NONCE_SIZE = 12


def hash_password(password):
    return generate_password_hash(password)


def is_password_hash(value):
    # werkzeug 해시는 "방식:파라미터$솔트$해시" 형태
    return value is not None and '$' in value and value.split(':', 1)[0] in ('scrypt', 'pbkdf2')


def normalize_rrn(rrn):
    # 하이픈 없이 13자리로 입력해도 같은 형식으로 맞춘다
    digits = rrn.strip().replace('-', '')
    if not (len(digits) == 13 and digits.isdigit()):
        raise ValueError('주민등록번호 형식이 올바르지 않습니다 (예: 900101-1234567)')
    return f'{digits[:6]}-{digits[6:]}'


def is_plain_rrn(value):
    return value is not None and RRN_PATTERN.match(value) is not None


def _load_key():
    # 키는 DB가 아니라 환경변수로 따로 둔다 (base64로 인코딩한 32바이트)
    key = base64.b64decode(os.environ['RRN_ENCRYPTION_KEY'])
    if len(key) != 32:
        raise ValueError('RRN_ENCRYPTION_KEY는 32바이트(AES-256) 키여야 합니다')
    return key


def encrypt_rrn(rrn):
    nonce = os.urandom(NONCE_SIZE)
    ciphertext = AESGCM(_load_key()).encrypt(nonce, normalize_rrn(rrn).encode(), None)
    return base64.b64encode(nonce + ciphertext).decode()


def decrypt_rrn(token):
    raw = base64.b64decode(token)
    return AESGCM(_load_key()).decrypt(raw[:NONCE_SIZE], raw[NONCE_SIZE:], None).decode()


def mask_rrn(rrn):
    # 화면에는 생년월일과 성별 자리까지만 보여준다
    return rrn[:8] + '*' * 6
