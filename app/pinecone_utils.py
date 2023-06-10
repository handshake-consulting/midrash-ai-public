""" Pinecone databse utilities """
import pinecone
from config import PineconeConfig

# pinecone init
pinecone.init(api_key=PineconeConfig.PINECONE_API_KEY,
              environment=PineconeConfig.PINECONE_ENVIRONMENT)
index = pinecone.Index(PineconeConfig.PINECONE_NAME)


def upsert_packages_to_pinecone(packages, pinecone_namespace):
    """ Upsert a package to pinecone at a rate of 50 a request. """
    upsert_packages = []
    for i, package in enumerate(packages):
        if i % 50 == 0 and i > 1:
            index.upsert(vectors=upsert_packages, namespace=pinecone_namespace)
            upsert_packages = []
            upsert_packages.append(package)
        else:
            upsert_packages.append(package)
    index.upsert(vectors=upsert_packages, namespace=pinecone_namespace)
