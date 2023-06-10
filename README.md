# futurebot-submit

This ended up just being futurebot but with cloud run capabilities.

url = https://interrogate-and-question-sad5uoukha-uc.a.run.app/

endpoints = {
  "/": {
    "methods": ["GET"],
    "returns": [index, javascript, images]
  }

  "/uploadfile": {
    "methods": ["GET"],
    "returns": [index, javascript, images]
  }

  "/submit": {
    "methods": ["POST"],
    "body": {"message": str},
    "returns": [Json : {
      "message": "some error message"
    },
      stream text good response, text/plain stream]
  }

  "/content": {
    "methods": ["POST"],
    "body": {"message": str},
    "returns": {
    document: document title
    documentcontent: document content
    input_id: "i"
    message : message equal to the message sent
    pinecone: hash of the message, id in pinecone
    }
  }

  "/upload": {
    "methods": ["POST"],
    "body": file object,
    "returns": [json response "message":"file uploaded"]
  }
}
