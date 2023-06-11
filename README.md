# Midrash AI Public

This ended up just being futurebot but with cloud run capabilities.

**URL:** https://midrash.ai

[<img src="https://midrash.ai/static//images/aiandfaith.jpg" alt="AI and Faith" height="100" width="100">](https://aiandfaith.org) [<img src="https://midrash.ai/static//images/handshake.jpg" alt="Handshake" height="100" width="100">](https://handshake.fyi)

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


## Guide for js functions

### 1. `askQuestion`

- **Function:** Handles form request to the backend
- **Properties:**
    - `searchValue`
    - `isLoading`
    - `isWaiting`
    - `result`
    - `reference`
    - `statusMessage`
    - `stream`
    - `refer`
    - `refcontent`
    - `text`
    - `abortController`
    - `ai`.
- **Methods:**
    1.  `handleSubmit`
        - Submits the form and updates the answer and reference content.
    2.  `getContent`
        - Fetches content based on the user prompt.

### 2. `typingAnimation`

- **Function:** Handles typing animation for generating, predicting and researching text.
- **Properties:**
    - `displayText`
    - `words`
    - `currentWordIndex`
    - `typingSpeed`
    - `deletingSpeed`
    - `pauseDuration`
    - `isDeleting`.

- **Methods:**
    1. `type`
        - Types the text with animation.
    2. `delete`
        - Deletes the text with animation.
    3. `sleep`
        - Sets a pause with input duration.
    4. `init`
        - Initializes the typing animation loop.

### 3. Global State Management

- **Store:** `globalState`
- **Properties:**
    - `showAnswer`
    - `showReference`
    - `showBookReference`
- **Methods:**
    1. `toggleAnswer`
        - Toggles answer visibility.
    2. `toggleReference`
        - Toggles reference visibility.
    3. `toggleBookReference`
        - Toggles book reference visibility.