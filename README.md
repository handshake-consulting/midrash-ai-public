# Midrash AI Public

Note: This was made for a conceptual research project in early 2023 and has not been updated since then. It is here for archival purposes only.

Midrash.ai is an experiment to explore the meaning of “truth” and “bias” in AI chatbots, using the Babylonian Talmud as an example. The Talmud is considered by some to be the canon interpretation of the Torah, which is in turn considered to be the source of absolute truth. The Talmud provides us with several useful characteristics to explore questions of bias and truth in AI chatbots:
-- Who are appropriate validators of truth? (e.g. Religious officials, The “crowd”, Ourselves)
-- Do we situate bias in a generative model in its ability to describe its underlying distribution, or its accordance with proper moral effect? 
-- The Talmud is an explicit “source of truth” in that its underlying values are directly declared. How does this help us examine the same questions for systems in which the underlying value systems are implicit, un-declared, or deliberately obscured?

You can access a hosted version of Midrash.ai here: https://midrash.ai

Midrash.ai is a partnership between Handshake (https://handshake.fyi) and AI and Faith (https://aiandfaith.org).

Midrash.ai is based on an English translation of the Babylonian Talmud by Michael L Rodkinson. The original PDF, and the OCR'd text, can be found here:
https://drive.google.com/drive/u/0/folders/176M_zubz3AktyL1H4wq8_7l6IpWOsLWw

MidrashBot uses a fairly standard architecture of retrieval-enhanced generation to produce its answers. An edition of the Babylonian Talmud is programmatically divided into chunks that are converted into searchable “embeddings.” When a question is posed to the system, it appends chunks into the prompt whose embeddings fall below a minimum vector distance from the question.


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
