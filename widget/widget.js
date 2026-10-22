(() => {
  "use strict";

  const script = document.currentScript;
  const widgetId = script?.dataset?.widgetId;
  const apiBase = script?.dataset?.apiBase || new URL(script.src).origin;

  if (!widgetId) {
    return console.error("[CollegeChatbot] Missing data-widget-id.");
  }

  let config = {
    name: "Chat bot",
    primary_color: "#4B52F5",
    welcome_message: "Hello! How can I help you today?",
    show_sources: true,
    show_feedback: true,
    suggested_questions: []
  };

  let sessionId = null;
  let root, messages, input, sendButton, chatWindow, launcher, lastMessageId;
  const iconUrl = `${apiBase}/icon.png`;

  const el = (tag, attrs = {}) => {
    const n = document.createElement(tag);

    for (const [k, v] of Object.entries(attrs)) {
      if (k === "text") {
        n.textContent = v;
      } else {
        n.setAttribute(k, v);
      }
    }

    return n;
  };

  function css() {
    return `
      :host {
        all: initial;
        font-family: Inter, system-ui, -apple-system, "Segoe UI", sans-serif;
      }

      *, *::before, *::after {
        box-sizing: border-box;
      }

      .launcher {
        position: fixed;
        right: 22px;
        bottom: 22px;
        z-index: 2147483647;
        width: 62px;
        height: 62px;
        border: 0;
        border-radius: 50%;
        background: ${config.primary_color};
        color: #fff;
        cursor: pointer;
        box-shadow: 0 12px 30px rgba(25, 32, 80, 0.25);
        font-size: 27px;
        display: grid;
        place-items: center;
        padding: 0;
      }

      .launcher img,
      .avatar img {
        width: 100%;
        height: 100%;
        display: block;
        object-fit: cover;
        border-radius: 50%;
      }

      .window {
        position: fixed;
        right: 22px;
        bottom: 22px;
        z-index: 2147483647;
        width: 390px;
        height: min(680px, calc(100vh - 44px));
        background: #fff;
        border-radius: 25px;
        overflow: hidden;
        box-shadow: 0 22px 60px rgba(20, 28, 60, 0.23);
        border: 1px solid #eef0f7;
        display: none;
        flex-direction: column;
      }

      .window.open {
        display: flex;
      }

      .header {
        padding: 18px 19px 14px;
        display: flex;
        align-items: center;
        gap: 12px;
        border-bottom: 1px solid #f1f2f6;
      }

      .avatar {
        width: 49px;
        height: 49px;
        border-radius: 50%;
        display: grid;
        place-items: center;
        overflow: hidden;
        background: linear-gradient(135deg, #57d7ff, #4b8cf7);
      }

      .headcopy {
        min-width: 0;
        flex: 1;
      }

      .title {
        font-size: 18px;
        font-weight: 800;
        color: #171b3a;
      }

      .subtitle {
        margin-top: 4px;
        font-size: 11px;
        color: #b6bac7;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
      }

      .close {
        border: 0;
        background: transparent;
        color: ${config.primary_color};
        font-size: 27px;
        cursor: pointer;
      }

      .messages {
        flex: 1;
        overflow-y: auto;
        padding: 18px 15px 14px;
        background: #fff;
      }

      .bubble {
        max-width: 88%;
        padding: 12px 15px;
        border-radius: 16px;
        margin: 8px 0;
        font-size: 14px;
        line-height: 1.45;
        white-space: pre-wrap;
      }

      .bot {
        background: #f0f1f4;
        color: #5f6471;
        border-top-left-radius: 5px;
      }

      .user {
        margin-left: auto;
        background: ${config.primary_color};
        color: #fff;
        border-top-right-radius: 5px;
      }

      .suggestions {
        display: flex;
        gap: 7px;
        overflow-x: auto;
        padding: 3px 0 10px;
        scrollbar-width: none;
      }

      .suggestion {
        border: 1px solid #e6e8ef;
        background: #fff;
        color: #656a78;
        border-radius: 15px;
        padding: 8px 10px;
        font-size: 11px;
        white-space: nowrap;
        cursor: pointer;
      }

      .sources {
        margin-top: 7px;
        font-size: 10px;
        color: #8d92a0;
      }

      .source {
        display: inline-block;
        margin: 4px 4px 0 0;
        padding: 4px 7px;
        border-radius: 8px;
        background: #f5f6fa;
      }

      .feedback {
        display: flex;
        align-items: center;
        justify-content: space-between;
        margin: 10px 2px 14px;
        padding: 9px 11px;
        border-radius: 20px;
        background: #e9efff;
        color: #9aa0b2;
        font-size: 11px;
      }

      .feedback button {
        width: 29px;
        height: 29px;
        border: 0;
        border-radius: 50%;
        background: #fff;
        cursor: pointer;
        margin-left: 4px;
      }

      .composer {
        margin: 0 13px 13px;
        border: 2px solid #78a0ff;
        border-radius: 17px;
        padding: 10px 11px 7px;
        background: #fff;
      }

      .composer-row {
        display: flex;
        align-items: flex-end;
        gap: 7px;
      }

      .input {
        flex: 1;
        min-height: 48px;
        max-height: 120px;
        border: 0;
        outline: 0;
        resize: none;
        font: 14px inherit;
        color: #4b5060;
        padding: 3px;
      }

      .input::placeholder {
        color: #c1c4cd;
      }

      .tool {
        border: 0;
        background: transparent;
        color: #a8adba;
        font-size: 19px;
        cursor: pointer;
        padding: 3px;
      }

      .send {
        border: 0;
        background: transparent;
        color: ${config.primary_color};
        font-size: 27px;
        cursor: pointer;
      }

      .send:disabled {
        opacity: 0.35;
      }

      .typing {
        display: inline-flex;
        gap: 4px;
      }

      .dot {
        width: 5px;
        height: 5px;
        border-radius: 50%;
        background: #aeb3c1;
        animation: b 1.1s infinite;
      }

      .dot:nth-child(2) {
        animation-delay: 0.15s;
      }

      .dot:nth-child(3) {
        animation-delay: 0.3s;
      }

      @keyframes b {
        0%, 70%, 100% {
          opacity: 0.25;
        }

        35% {
          opacity: 1;
        }
      }

      @media (max-width: 560px) {
        .window {
          inset: 0;
          width: 100%;
          height: 100%;
          border-radius: 0;
        }

        .launcher {
          right: 16px;
          bottom: 16px;
        }
      }
    `;
  }

  function addMessage(text, who, sources) {
    const b = el("div", { class: `bubble ${who}`, text });
    messages.appendChild(b);

    if (sources?.length) {
      const s = el("div", { class: "sources", text: "Sources: " });
      sources.forEach((x) => {
        s.appendChild(
          el("span", {
            class: "source",
            text: x.page ? `${x.title} · p.${x.page}` : x.title
          })
        );
      });
      messages.appendChild(s);
    }

    messages.scrollTop = messages.scrollHeight;
  }

  async function feedback(value) {
    try {
      await fetch(`${apiBase}/api/v1/feedback`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          widget_id: widgetId,
          session_id: sessionId,
          message_id: lastMessageId,
          feedback: value
        })
      });
    } catch (_e) {
      // Ignore feedback failures.
    }
  }

  function addFeedback() {
    if (!config.show_feedback) return;

    const wrap = el("div", { class: "feedback" });
    const label = el("span", { text: "Did you like the answer?" });
    const box = el("span");
    const up = el("button", { title: "Helpful", text: "👍" });
    const down = el("button", { title: "Not helpful", text: "👎" });

    up.onclick = () => feedback("up");
    down.onclick = () => feedback("down");

    box.append(up, down);
    wrap.append(label, box);
    messages.appendChild(wrap);
  }

  function typing(show) {
    const old = messages.querySelector("[data-typing]");
    if (old) old.remove();
    if (!show) return;

    const b = el("div", { class: "bubble bot" });
    b.dataset.typing = "1";
    b.innerHTML = '<span class="typing"><span class="dot"></span><span class="dot"></span><span class="dot"></span></span>';
    messages.appendChild(b);
    messages.scrollTop = messages.scrollHeight;
  }

  async function sendMessage(raw) {
    const value = (raw ?? input.value).trim();
    if (!value) return;

    input.value = "";
    input.style.height = "48px";
    addMessage(value, "user");
    sendButton.disabled = true;
    typing(true);

    try {
      const r = await fetch(`${apiBase}/api/v1/chat`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          widget_id: widgetId,
          session_id: sessionId,
          message: value
        })
      });
      const data = await r.json();
      typing(false);

      if (!r.ok) {
        throw new Error(data.detail || "Request failed");
      }

      sessionId = data.session_id;
      lastMessageId = Date.now().toString();
      addMessage(data.answer, "bot", data.sources);
      addFeedback();
    } catch (e) {
      typing(false);
      addMessage("I'm temporarily unable to answer your question. Please try again shortly.", "bot");
    } finally {
      sendButton.disabled = false;
      input.focus();
    }
  }

  async function loadConfig() {
    try {
      const r = await fetch(`${apiBase}/api/v1/widget/${encodeURIComponent(widgetId)}/config`);
      if (r.ok) {
        config = await r.json();
      }
    } catch (_e) {
      // Ignore config fetch failures and keep defaults.
    }
  }

  function build() {
    const host = document.createElement("div");
    root = host.attachShadow({ mode: "open" });

    const style = document.createElement("style");
    style.textContent = css();
    root.appendChild(style);

    launcher = el("button", { class: "launcher", "aria-label": "Open chat" });
    const launcherImage = el("img", { src: iconUrl, alt: "Chatbot icon" });
    launcher.appendChild(launcherImage);
    chatWindow = el("section", { class: "window", "aria-label": "College chatbot" });

    const header = el("header", { class: "header" });
    const avatar = el("div", { class: "avatar" });
    const avatarImage = el("img", { src: iconUrl, alt: "Assistant avatar" });
    avatar.appendChild(avatarImage);
    const copy = el("div", { class: "headcopy" });

    copy.append(
      el("div", { class: "title", text: config.name || "Chat bot" }),
      el("div", { class: "subtitle", text: "I'm your online assistant." })
    );

    const close = el("button", { class: "close", "aria-label": "Close chat", text: "⌄" });
    close.onclick = () => {
      chatWindow.classList.remove("open");
      launcher.style.display = "grid";
    };

    header.append(avatar, copy, close);

    messages = el("div", { class: "messages" });
    addMessage(config.welcome_message || "Hello! How can I help you today?", "bot");

    if (config.suggested_questions?.length) {
      const row = el("div", { class: "suggestions" });
      config.suggested_questions.forEach((q) => {
        const b = el("button", { class: "suggestion", text: q });
        b.onclick = () => sendMessage(q);
        row.appendChild(b);
      });
      messages.appendChild(row);
    }

    const composer = el("div", { class: "composer" });
    const row = el("div", { class: "composer-row" });

    input = el("textarea", {
      class: "input",
      placeholder: "Ask anything...",
      "aria-label": "Ask anything"
    });
    input.rows = 1;
    input.oninput = () => {
      input.style.height = "48px";
      input.style.height = `${Math.min(input.scrollHeight, 120)}px`;
    };
    input.onkeydown = (e) => {
      if (e.key === "Enter" && !e.shiftKey) {
        e.preventDefault();
        sendMessage();
      }
    };

    const tools = el("div");
    const emoji = el("button", { class: "tool", title: "Emoji", text: "☺" });
    const attach = el("button", { class: "tool", title: "Attachment", text: "⌕" });

    emoji.onclick = () => {
      input.value += "🙂";
    };
    attach.onclick = () => {
      alert("Connect this button to your file/knowledge ingestion service.");
    };

    sendButton = el("button", { class: "send", "aria-label": "Send message", text: "➤" });
    sendButton.onclick = () => sendMessage();

    tools.append(emoji, attach);
    row.append(input, tools, sendButton);
    composer.append(row);

    chatWindow.append(header, messages, composer);
    root.append(launcher, chatWindow);

    launcher.onclick = () => {
      chatWindow.classList.add("open");
      launcher.style.display = "none";
      setTimeout(() => input.focus(), 50);
    };

    document.body.appendChild(host);
  }

  (async () => {
    await loadConfig();
    build();
  })();
})();
