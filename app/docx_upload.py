""" docx specific utilites """


def create_document_dict(document_title, texts):
    """ create a document dict for upsert to pinecone """
    document_dict = {"title": document_title}
    for chunk_index, text in enumerate(texts):
        document_dict[chunk_index] = {}
        document_dict[chunk_index]['content'] = text
    return document_dict
