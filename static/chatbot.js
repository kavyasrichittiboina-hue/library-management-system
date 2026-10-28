
document.addEventListener("DOMContentLoaded", () => {
  const chatButton = document.getElementById("library-chat-toggle");
  const chatPanel = document.getElementById("library-chat-panel");
  const chatForm = document.getElementById("library-chat-form");
  const chatInput = document.getElementById("library-chat-input");
  const chatMessages = document.getElementById("library-chat-messages");

  if (!chatButton || !chatPanel || !chatForm || !chatInput || !chatMessages) {
    console.error("Library chatbot HTML elements are missing.");
    return;
  }

  function addMessage(text, sender) {
    const message = document.createElement("div");
    message.className = `library-chat-message ${sender}`;
    message.textContent = text;
    chatMessages.appendChild(message);
    chatMessages.scrollTop = chatMessages.scrollHeight;
    return message;
  }

  
chatButton.addEventListener("click", () => {
    const panelIsClosed = chatPanel.hidden;

    chatPanel.hidden = !panelIsClosed;

    chatButton.setAttribute(
        "aria-expanded",
        panelIsClosed ? "true" : "false"
    );

    console.log("Library chatbot panel open:", panelIsClosed);

    if (panelIsClosed && chatInput) {
        chatInput.focus();
    }
});


  chatForm.addEventListener("submit", async (event) => {
    event.preventDefault();

    const question = chatInput.value.trim();
    if (!question) return;

    addMessage(question, "user");
    chatInput.value = "";
    chatInput.disabled = true;

    const loadingMessage = addMessage("Thinking…", "assistant");

    try {
      const response = await fetch("/api/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ question })
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.detail || "The chatbot request failed.");
      }

      loadingMessage.textContent =
        data.answer || "Sorry, I couldn't generate an answer.";
    } catch (error) {
      console.error("Chatbot request failed:", error);
      loadingMessage.textContent =
        "Sorry, the chatbot is temporarily unavailable. Please try again.";
    } finally {
      chatInput.disabled = false;
      chatInput.focus();
      chatMessages.scrollTop = chatMessages.scrollHeight;
    }
  });
});
