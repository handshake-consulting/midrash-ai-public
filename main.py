""" Chatbot server """
import os
import time
import uuid
from flask import Flask, jsonify, Response, request, make_response
from flask import render_template

from google.cloud import storage
from google.api_core.exceptions import NotFound

from app.lang_wizard import LangWizard
from app.database_adapters import PineconeDatabaseAdapter
from app.ai_adapters import OpenAIAdapter, Ai21Adapter
from app.storage_adapters import GoogleBucketStorage
# from app.login import password_hash, password_login, password_hash_login
from app.sha_hash import hash_message_sha_256
from app.openai_utils import get_openai_embeddings

from config import PineconeConfig, OpenAIConfig, AI21Config, AppConfig

storage_client = storage.Client()

app = Flask(__name__)

@app.route('/')
def root():
    """ Render root """
    response = make_response(render_template('index.html', gtm_container_id=AppConfig.GTM_CONTAINER_ID))
    response.set_cookie("username", str(uuid.uuid4()), httponly=True)
    return response


@app.errorhandler(404)
def page_not_found(error):
    """ 404 error page """
    return render_template('404.html'), 404


@app.route("/content", methods=['POST', 'OPTIONS'])
def content():
    """ Return a piece of content based on the message request """
    # Set CORS headers for preflight requests
    if request.method == 'OPTIONS' or request.method == 'OPTION':
        headers = {
            'Access-Control-Allow-Origin': "*",
            'Access-Control-Allow-Methods': 'POST',
            'Access-Control-Allow-Headers': '*',
            'Access-Control-Max-Age': '*'
        }
        return ('', 204, headers)

    json_data = request.get_json()
    message = json_data['message']
    message_hash = hash_message_sha_256(message)
    # token = request.cookies.get('token')
    # if not password_hash_login(token):
    #     response = jsonify({"message": "Please login to use this service."})
    #     response.headers['Access-Control-Allow-Origin'] = '*'
    #     return response
    message = json_data['message']
    username = request.cookies.get('username')

    active_retry = True
    retry_number = 0
    while active_retry:
        try:
            bucket_storage = GoogleBucketStorage(storage_client, AppConfig.BUCKET_NAME)
            dirty_payload = bucket_storage.fetch([message_hash, username] \
                                                 + PineconeConfig.PINECONE_NAMESPACES)
            response = jsonify(dirty_payload)
            response.headers['Access-Control-Allow-Origin'] = '*'
            return response
        except NotFound:
            print("waiting on file")
            time.sleep(10)
            retry_number += 1
            if retry_number > 10:
                active_retry = False
    response = jsonify({
        "message": "Failed to find file.  This is usually \
                    due to this function being called too quickly."
        })
    response.headers['Access-Control-Allow-Origin'] = '*'
    return response


@app.route("/submit", methods=['POST', 'OPTIONS'])
def submit():
    """ Return a streamed response from the langwizard based on the submit endpoint """
    # Set CORS headers for preflight requests
    if request.method == 'OPTIONS' or request.method == 'OPTION':
        headers = {
            'Access-Control-Allow-Origin': "*",
            'Access-Control-Allow-Methods': 'POST',
            'Access-Control-Allow-Headers': '*',
            'Access-Control-Max-Age': '*'
        }
        return ('', 204, headers)

    json_data = request.get_json()
    # token = request.cookies.get('token')
    # if not password_hash_login(token):
    #     response = jsonify("message", "Please login to use this service.")
    #     response.headers['Access-Control-Allow-Origin'] = '*'
    #     return response
    message = json_data['message']
    username = request.cookies.get("username")
    if username is None:
        username = "NoTrackUsername"

    pinecone_adapter = PineconeDatabaseAdapter(PineconeConfig, get_openai_embeddings, False)
    if "namespace" in json_data:
        pinecone_adapter.set_namespace(json_data['namespace'])

    ai_name = None
    if "ai" in json_data:
        ai_name = json_data["ai"]

    openai_adapter = OpenAIAdapter(OpenAIConfig)
    ai21_adapter = Ai21Adapter(AI21Config)
    bucket_storage = GoogleBucketStorage(storage_client, AppConfig.BUCKET_NAME)

    wizard = LangWizard(endpoints_yaml_path='endpoints.yaml',
                        rollback_query_max=1,
                        surrounding_special="__",
                        ai_adapters={"openai": openai_adapter, "ai21": ai21_adapter},
                        pinecone_adapter=pinecone_adapter,
                        storage_adapter=None,
                        rollback_token_length=3500)

    namespace_key = "|".join(pinecone_adapter.get_selected_namespaces())
    output, _, storage_json = wizard.endpoint_responce('submit',
                                            message=message,
                                            storage_keys=[username, namespace_key],
                                            ai_adapter=ai_name)

    if AppConfig.STREAM:
        print("STREAMING")
        def response_generator(output, storage_json, storage_adapter):
            output_total = ""
            for chunk in output:
                output_total += chunk
                yield chunk
            payload = storage_json['payload']
            payload['output'] = output_total
            storage_adapter.store(payload, storage_json['keys'])

        return Response(response_generator(output, storage_json, bucket_storage),
                        mimetype='text/event-stream',
                        headers={'X-Accel-Buffering': 'no',
                                 'Access-Control-Allow-Origin': '*'})

    response = jsonify({"message": output})
    # Set CORS headers for the main request
    response.headers['Access-Control-Allow-Origin'] = '*'

    return response

# @app.route('/tokengeneration', methods=['GET'])
# def token_generation():
#     return render_template('tokengeneration.html')


# @app.route('/tokengenerate', methods=['POST', 'OPTIONS'])
# def token_generate():
#     # Set CORS headers for preflight requests
#     if request.method == 'OPTIONS':
#         headers = {
#             'Access-Control-Allow-Origin': "*",
#             'Access-Control-Allow-Methods': 'POST',
#             'Access-Control-Allow-Headers': '*',
#             'Access-Control-Max-Age': '*'
#         }
#         return ('', 204, headers)

#     json_data = request.get_json()
#     message = json_data['message']

#     if password_login(message):
#         message_hash = password_hash(message)
#         response = jsonify({"message": "accepted"})
#         response.set_cookie("token", message_hash, httponly=True)
#         response.set_cookie("username", str(uuid.uuid4()), httponly=True)
#         response.headers['Access-Control-Allow-Origin'] = '*'
#         return response
#     response = jsonify({"message": "denied"})
#     response.set_cookie("token", "denied", httponly=True)
#     response.headers['Access-Control-Allow-Origin'] = '*'
#     return response


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))
