""" Hashing utilities """
import hashlib

def hash_message_sha_256(message):
    """ Hash a message to sha 256 """
    message = message.encode(encoding="ASCII", errors="ignore")
    return hashlib.sha256(bytes(message)).hexdigest()
