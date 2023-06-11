# Midrash AI Public

This ended up just being futurebot but with cloud run capabilities.

**URL:** https://midrash.ai

<img src="https://midrash.ai/static//images/aiandfaith.jpg" alt="AI and Faith" height="80" width="80"> **X** <img src="https://midrash.ai/static//images/handshake.jpg" alt="Handshake" height="80" width="80">

## Endpoints:

### 1. `/`

- **Methods:** `GET`
- **Returns:**
  - index
  - JavaScript
  - images

### 2. `/submit`

- **Methods:** `POST`
- **Body:**
  - `message`: string
  -`ai`: string (openai or ai)
- **Returns:**
  - Stream text good response, text/plain stream

### 3. `/content`

- **Methods:** `POST`
- **Body:**
  - `message`: string
- **Returns:**
  - `document`: document title
  - `documentcontent`: document content
  - `input_id`: "i"
  - `message`: message equal to the message sent
  - `pinecone`: hash of the message, id in pinecone