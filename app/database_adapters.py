""" Database adapters for the langwizard """
import re
import time
import pinecone
from pinecone.exceptions import PineconeProtocolError

from app.sha_hash import hash_message_sha_256

from config import PineconeConfig

pinecone.init(api_key=PineconeConfig.PINECONE_API_KEY,
              environment=PineconeConfig.PINECONE_ENVIRONMENT)
index = pinecone.Index(PineconeConfig.PINECONE_NAME)


class DatabaseAdapter:
    """ Database adapter used for the langwizard to query details """

    def query(self, message):
        """ Get content based on some message to a databse """
        raise NotImplementedError

    def create_id(self, message):
        """ Generate an id for the database """
        raise NotImplementedError

    def pull_key_from_responses(self, responses, key):
        """ Given a set of reponses get a certain piece of data based on a key """
        raise NotImplementedError

    def pull_id_from_reponses(self, responses):
        """ Given a set of reponses get an id """
        raise NotImplementedError


class PineconeDatabaseAdapter(DatabaseAdapter):
    """ Pinecone databse adapter used for the langwizard """

    def create_id(self, message):
        message = message.encode(encoding="ASCII", errors="ignore").decode()
        return hash_message_sha_256(message)

    @staticmethod
    def split_key(key, split='/'):
        """ Split the keys that are incoming from langwizard """
        return re.split(split, key)

    def __init__(self, config, embedding_function, global_index=True):
        if global_index:
            self.index = None
        else:
            pinecone.init(api_key=config.PINECONE_API_KEY, environment=config.PINECONE_ENVIRONMENT)
            self.index = pinecone.Index(config.PINECONE_NAME)
        self.embedding_function = embedding_function
        self.namespaces = config.PINECONE_NAMESPACES
        self.top_k = config.NUM_QUERY_RESPONSE
        self.selected_namespace = config.PINECONE_NAMESPACES

    def global_index(self):
        """ Use the global index most of the time """
        if self.index is not None:
            return self.index
        return index

    def pinecone_message_upsert(self, message, vector, namespace='messages'):
        """ Upsert a message into pinecone """
        pinecone_index = self.global_index()
        message_dict = [{
            "id": self.create_id(message),
            "values": vector,
            "metadata": {
                "message": message
            }
        }]
        pinecone_index.upsert(vectors=message_dict, namespace=namespace)

    def fetch_pinecone_embedding(self, message_hash, namespace='messages', max_retry=5):
        """ Fetch a given embedding from pinecone, wrapped in retry if a single instance get's bombarded by traffic."""
        pinecone_index = self.global_index()
        retry = 0
        while True:
            try:
                return pinecone_index.fetch(ids=[message_hash], namespace=namespace)['vectors']
            except PineconeProtocolError:
                print("Pinecone is overburdened.")
                retry += 1
                if retry > max_retry:
                    return False
                time.sleep(2.5)

    def get_message_embeddings(self, message):
        """ retieve message embeddings or use an embedding function """
        message_hash = self.create_id(message)
        pinecone_responce = self.fetch_pinecone_embedding(message_hash, 'messages')
        if pinecone_responce:
            message_vector = pinecone_responce[message_hash]['values']
        else:
            message_vector = self.embedding_function(message)
            self.pinecone_message_upsert(message, message_vector)
        return message_vector

    def query_pinecone(self, vector, namespace, top_k=5):
        """ Query pinecone for a set of responses """
        pinecone_index = self.global_index()
        query_response = pinecone_index.query(
            namespace=namespace,
            top_k=top_k,
            include_values=False,
            include_metadata=True,
            vector=vector)
        return query_response['matches']

    def query_many(self, vector, namespaces, top_k=3):
        """ Query a few namespaces """
        matches = []
        for namespace in namespaces:
            matches += self.query_pinecone(vector, namespace, top_k)
        return matches

    def get_selected_namespaces(self):
        """ getter for selected namespace """
        return self.selected_namespace

    def set_namespace(self, namespaces):
        """ set the namespace that should be used  note that the namespace must
            be in the set of namespaces given at init
        """
        temp_namespaces = [namespace for namespace in namespaces if namespace in self.namespaces]
        if temp_namespaces:
            self.selected_namespace = temp_namespaces
            return temp_namespaces
        return self.namespaces

    def query(self, message):
        message_vector = self.get_message_embeddings(message)
        namespaces = self.selected_namespace
        return self.query_many(message_vector, namespaces, self.top_k)

    def pull_key_from_responses(self, responses, key):
        keys = self.split_key(key)
        found_keys = []
        for response in responses:
            temp_return = response
            append = True
            for key in keys:
                try:
                    temp_return = temp_return[key]
                except KeyError as key_error:
                    print(f'key not found {key_error}')
                    append = False
            if append:
                found_keys.append(temp_return)
        return found_keys

    def pull_id_from_reponses(self, responses):
        ids = []
        for response in responses:
            ids.append(response['id'])
        return ids


class InputAdapter(DatabaseAdapter):

    def query(self, message):
        return [message]

    def pull_key_from_responses(self, responses, key):
        return responses

    def pull_id_from_reponses(self, responses):
        return "input"

    def create_id(self, message):
        return "input"
