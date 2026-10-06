let conversationId = null;


// =========================================
// INITIALIZE
// =========================================

window.onload = async function () {

    await createConversation();

};


// =========================================
// CREATE NEW CONVERSATION
// =========================================

async function createConversation() {

    try {

        const response = await fetch(
            "/conversations",
            {
                method: "POST"
            }
        );

        const data = await response.json();

        conversationId = data.conversation_id;

        addConversationToSidebar(
            conversationId
        );

    } catch (error) {

        console.error(
            "Could not create conversation:",
            error
        );

    }

}


// =========================================
// NEW CHAT BUTTON
// =========================================

async function newChat() {

    clearMessages();

    await createConversation();

}


// =========================================
// ADD CONVERSATION TO SIDEBAR
// =========================================

function addConversationToSidebar(id) {

    const list =
        document.getElementById(
            "conversationList"
        );


    const item =
        document.createElement("div");

    item.className =
        "conversation-item";


    item.textContent =
        `Conversation ${id}`;


    item.onclick = function () {

        loadConversation(id);

    };


    list.prepend(item);

}


// =========================================
// LOAD CONVERSATION
// =========================================

async function loadConversation(id) {

    try {

        const response = await fetch(
            `/conversations/${id}`
        );

        const data =
            await response.json();


        conversationId = id;

        clearMessages();


        data.messages.forEach(
            message => {

                if (
                    message.role === "user"
                ) {

                    addMessage(
                        message.content,
                        "user"
                    );

                }

                else if (
                    message.role === "assistant"
                ) {

                    addMessage(
                        message.content,
                        "assistant"
                    );

                }

            }
        );


    } catch (error) {

        console.error(
            "Could not load conversation:",
            error
        );

    }

}


// =========================================
// SEND MESSAGE
// =========================================

async function sendMessage() {

    const input =
        document.getElementById(
            "messageInput"
        );

    const button =
        document.getElementById(
            "sendButton"
        );


    const message =
        input.value.trim();


    if (!message) {
        return;
    }


    // Show user message
    addMessage(
        message,
        "user"
    );


    input.value = "";

    input.style.height = "auto";

    button.disabled = true;


    // Show loading
    const loading =
        addMessage(
            "Thinking...",
            "assistant"
        );


    try {

        const response =
            await fetch(
                "/chat",
                {
                    method: "POST",

                    headers: {
                        "Content-Type":
                            "application/json"
                    },

                    body: JSON.stringify({

                        conversation_id:
                            conversationId,

                        message:
                            message

                    })
                }
            );


        const data =
            await response.json();


        // Remove loading message
        loading.remove();


        if (data.error) {

            addMessage(
                "Sorry, something went wrong: "
                + data.error,
                "assistant"
            );

        }

        else {

            addMessage(
                data.answer,
                "assistant"
            );

        }


    } catch (error) {

        loading.remove();

        addMessage(
            "Unable to connect to the AI agent.",
            "assistant"
        );

        console.error(error);

    }


    button.disabled = false;

    input.focus();

}


// =========================================
// ADD MESSAGE
// =========================================

function addMessage(
    text,
    sender
) {

    const messages =
        document.getElementById(
            "messages"
        );


    // Remove welcome screen
    const welcome =
        document.querySelector(
            ".welcome"
        );

    if (welcome) {
        welcome.remove();
    }


    const message =
        document.createElement(
            "div"
        );


    message.className =
        `message ${sender}`;


    const content =
        document.createElement(
            "div"
        );


    content.className =
        "message-content";


    content.textContent =
        text;


    message.appendChild(
        content
    );


    messages.appendChild(
        message
    );


    // Scroll to bottom
    messages.scrollTop =
        messages.scrollHeight;


    return message;

}


// =========================================
// CLEAR MESSAGES
// =========================================

function clearMessages() {

    const messages =
        document.getElementById(
            "messages"
        );


    messages.innerHTML = `

        <div class="welcome">

            <div class="welcome-icon">
                ✨
            </div>

            <h2>
                How can I help you?
            </h2>

            <p>
                Ask me anything. I can use tools,
                remember important information,
                and solve multi-step tasks.
            </p>

            <div class="suggestions">

                <button
                    onclick="useSuggestion(
                        'Calculate 25 multiplied by 16'
                    )"
                >
                    🧮 Calculate something
                </button>

                <button
                    onclick="useSuggestion(
                        'What is the weather in Pune?'
                    )"
                >
                    🌤️ Check weather
                </button>

                <button
                    onclick="useSuggestion(
                        'Remember that my favorite language is C++'
                    )"
                >
                    🧠 Save a memory
                </button>

            </div>

        </div>

    `;

}


// =========================================
// SUGGESTION BUTTON
// =========================================

function useSuggestion(text) {

    const input =
        document.getElementById(
            "messageInput"
        );


    input.value = text;

    input.focus();

}


// =========================================
// ENTER KEY
// =========================================

function handleKey(event) {

    if (
        event.key === "Enter"
        &&
        !event.shiftKey
    ) {

        event.preventDefault();

        sendMessage();

    }

}