""" Google buckets utils | Store, Fetch, Fetch/Delete. """
import json

def create_primary_key(keys, sep="|"):
    """ joins a list based on a seperator """
    return sep.join(keys)

def store_blob(storage_client, bucket_name, payload, keys, sep="|"):
    """ Stores a payload in a bucket with a list of keys used as a blob title """
    bucket = storage_client.get_bucket(bucket_name)
    blob = bucket.blob(create_primary_key(keys, sep=sep))
    blob.upload_from_string(
        data=json.dumps(payload),
        content_type="application/json"
    )

def fetch_blob(storage_client, bucket_name, keys, sep="|"):
    """ fetches the contents of a blob from GCP buckets """
    bucket = storage_client.get_bucket(bucket_name)
    blob = bucket.blob(create_primary_key(keys, sep=sep))
    contents = json.loads(blob.download_as_string())
    return contents

def fetch_delete_blob(storage_client, bucket_name, keys, sep="|"):
    """ fetches the contents of a blob and deletes it """
    bucket = storage_client.get_bucket(bucket_name)
    blob = bucket.blob(create_primary_key(keys, sep=sep))
    contents = json.loads(blob.download_as_string())
    blob.reload()  # Fetch blob metadata to use in generation_match_precondition.
    generation_match_precondition = blob.generation
    blob.delete(if_generation_match=generation_match_precondition)
    return contents
