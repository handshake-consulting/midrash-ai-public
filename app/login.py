""" Used to generate login information, declutter main."""
from google.auth.transport import requests
import google.oauth2.id_token

import bcrypt

from config import AppConfig


firebase_request_adapter = requests.Request()

def is_logged_in(id_token):
    if AppConfig.STAGE == "dev" and (id_token == '' or id_token is None):
        return "DEVELOPMENT_CLAIM"
    if id_token != "":
        try:
            claims = google.oauth2.id_token.verify_firebase_token(
                id_token, firebase_request_adapter)
            return claims
        except ValueError:
            return None
    return None


def password_hash(token):
    if token != "":
        try:
            password = token.encode("utf-8")
            encrypted_hash = bcrypt.hashpw(password=password,
                                           salt=bcrypt.gensalt(10))
            return encrypted_hash
        except ValueError:
            return None
    return None


def password_login(token):
    if token != "":
        return bcrypt.checkpw(AppConfig.HASH.encode("utf-8"),
                              password_hash(token))
    return False


def password_hash_login(token_hash):
    if token_hash is None or token_hash == "":
        return False
    try:
        return bcrypt.checkpw(AppConfig.HASH.encode("utf-8"),
                          bytes(token_hash.encode("utf-8")))
    except ValueError:  #catch for bad hash
        return False

def hash_check(token_hash):
    if token_hash != "":
        return bytes(AppConfig.HASH.encode('utf-8')) == token_hash
