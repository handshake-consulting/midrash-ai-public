""" Pinecone file upload utilities used accross all filetypes """
from app.sha_hash import hash_message_sha_256
from app.openai_utils import get_openai_embeddings


def generate_pinecone_presentation_upsert(document_title, chunk_index, content, vector):
    """ Upsert documents to pinecone presentation difference """
    chunk_dict = {}
    chunk_dict["id"] = hash_message_sha_256(content)
    chunk_dict["values"] = vector
    metadata = {}
    metadata['title'] = document_title
    metadata['chunk_index'] = chunk_index
    metadata['content'] = content
    chunk_dict["metadata"] = metadata
    return chunk_dict

def generate_upsert_package(document_dict):
    """ Create a package upsert, can be directly sent to pinecone """
    packages = []
    document_title = document_dict['title']
    for chunk_index in [document_name for document_name in list(document_dict.keys()) if document_name != "title"]:
        content = document_dict[chunk_index]['content']
        vector = get_openai_embeddings(content, engine="text-embedding-ada-002")
        document_dict[chunk_index]['vector'] = vector
        package = generate_pinecone_presentation_upsert(document_title, chunk_index, content, vector)
        packages.append(package)
    return packages, document_dict
