""" Storage adapters for the langwizard """
from app.bucket import store_blob, fetch_blob


class StorageAdapter:
    """ used by the langwizard to store payloads in databases """

    def store(self, payload_json, keys):
        """ Store a payload in a database with an id keys """
        raise NotImplementedError

    def fetch(self, key):
        """ Get an item in the database based on some keys """
        raise NotImplementedError

class GoogleBucketStorage(StorageAdapter):
    """ Storage bucket adapter for GCP buckets """

    def __init__(self, storage_client, bucket_name):
        self.storage_client = storage_client
        self.bucket_name = bucket_name

    def store(self, payload_json, keys):
        store_blob(self.storage_client, self.bucket_name, payload_json, keys)

    def fetch(self, key):
        return fetch_blob(self.storage_client, self.bucket_name, key)
