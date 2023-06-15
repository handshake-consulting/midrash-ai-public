"use strict";


// handle form request to backend

function askQuestion() {
  return {
    searchValue: "",
    isLoading: false,
    isWaiting: false,
    result: "",
    reference: "",
    statusMessage: "",
    stream: "",
    token: "",
    refer: false,
    refcontent: "",
    text: "Lorem ipsum dolor sit amet, consectetur",
    abortController: new AbortController(),
    ai: "openai",
    async handleSubmit() {
      this.abortController = new AbortController(); // Reset the abort controller
      this.result = "";
      this.reference = "";
      this.stream = "";
      this.refcontent = "";
      // Show the Answer component after submitting the form
      if (this.searchValue.trim().length === 0) {
        alert("Enter Text");
        return;
      }

      if (this.ai === null) {
        alert("Select Ai Model");
        return;
      }
      if (Alpine.store("globalState").showAnswer) {
        Alpine.store("globalState").toggleAnswer();
        Alpine.store("globalState").toggleReference(false);
      }
      this.isLoading = true;
      this.isWaiting = true;
      //  this.token = getCookie('token')
      try {
        // console.log('fetching');
        const response = await fetch("/submit", {
          method: "POST",
          body: JSON.stringify({
            message: this.searchValue,
            ai: this.ai,
          }),
          headers: {
            "Content-Type": "application/json",
          },
          signal: this.abortController.signal,
        });

        if (!response.ok) {
          const json = await response.text();
          throw new Error(json);
        }

        const data = response.body;
        if (!data) {
          return;
        }

        await this.getContent(this.searchValue);
        const reader = data.pipeThrough(new TextDecoderStream()).getReader();
        Alpine.store("globalState").toggleAnswer();
        this.isWaiting = false;
        while (true) {
          const { value, done } = await reader.read();
          if (done) {

            if (this.refcontent.trim() !== "") {
              Alpine.store("globalState").toggleReference(true);
            }

            this.isLoading = false;
            break;
          }

          this.result += value;
        }
      } catch (error) {
        // Check if the error is caused by request cancellation
        if (error.name === "AbortError") {
          this.isLoading = false;
          this.statusMessage = "Request cancelled";
          this.isWaiting = false;
        } else {
          this.isLoading = false;
          console.error("Error:", error);
          this.statusMessage = error;
          this.isWaiting = false;
        }
      }
    },
    async getContent(userprompt) {
      try {
        const response = await fetch("/content", {
          method: "POST",
          body: JSON.stringify({
            message: userprompt,
          }),
          headers: {
            "Content-Type": "application/json",
          },
        });
        const data = await response.json();

        // checks if response returns empty reference data , do nothing if data is empty
        if (data.documentcontent.toString().replace(",", " ") !== "") {
          this.refcontent = data.documentcontent.toString().replace(",", " ");
          this.reference = data.document.toString().replace(",", " ");
        }
      } catch (error) {
        console.error("Error:", error);
      }
    },
    cancelRequest() {
      this.abortController.abort(); // Abort the fetch request
    },
  };
}
// handle form request to backend end

// handle typing animation
function typingAnimation() {
  return {
    displayText: "",
    words: ["Generating", "Predicting", "Researching"],
    currentWordIndex: 0,
    typingSpeed: 150,
    deletingSpeed: 100,
    pauseDuration: 1000,
    isDeleting: false,

    async type(currentText, wordIndex) {
      for (let i = 0; i < currentText.length; i++) {
        if (this.currentWordIndex !== wordIndex) return;
        this.displayText = currentText.substr(0, i + 1);
        await this.sleep(this.typingSpeed);
      }
    },

    async delete(currentText, wordIndex) {
      for (let i = currentText.length; i > 0; i--) {
        if (this.currentWordIndex !== wordIndex) return;
        this.displayText = currentText.substr(0, i - 1);
        await this.sleep(this.deletingSpeed);
      }
    },

    async sleep(ms) {
      return new Promise((resolve) => {
        setTimeout(() => resolve(), ms);
      });
    },

    async init() {
      while (true) {
        const currentText = this.words[this.currentWordIndex];
        const wordIndex = this.currentWordIndex;
        await this.type(currentText, wordIndex);
        await this.sleep(this.pauseDuration);
        await this.delete(currentText, wordIndex);
        await this.sleep(this.pauseDuration);
        this.currentWordIndex = (this.currentWordIndex + 1) % this.words.length;
      }
    },
  };
}



// global state management start

document.addEventListener("alpine:init", () => {
  Alpine.store("globalState", {
    showAnswer: false,
    showReference: false,
    showBookReference: false,
    toggleAnswer() {
      this.showAnswer = !this.showAnswer;
    },
    toggleReference(status) {
      this.showReference = status;
    },
    toggleBookReference() {
      this.showBookReference = !this.showBookReference;
    },
  });
});

// global state managment end
