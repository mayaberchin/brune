import { useEffect, useRef, useState } from "react";
import ClassFilter, { MobileClassFilter } from "../components/ClassFilter";

function getChatWebSocketUrl() {
  let protocol = "ws:";
  let host = window.location.host;

  if (window.location.protocol === "https:") {
    protocol = "wss:";
  }
  if (window.location.hostname === "localhost" || window.location.hostname === "127.0.0.1") {
    host = window.location.hostname + ":3030";
  }

  return protocol + "//" + host + "/ws/chat";
}

function ChatLayout({
  classes,
  posts,
  selectedPostType,
  currentUserEmail,
  addPost,
  addLivePost,
}) {
  const [selectedClassId, setSelectedClassId] = useState("");
  const [msg, setMsg] = useState("");
  const [atBottom, setAtBottom] = useState(true);
  const socketRef = useRef(null);
  const messagesRef = useRef(null);
  const selectedClassIdRef = useRef(selectedClassId);
  const lastClassRef = useRef(selectedClassId);
  selectedClassIdRef.current = selectedClassId;

  useEffect(() => {
    if (selectedClassId === "" && classes.length > 0) {
      setSelectedClassId(String(classes[0].class_id));
    }
  }, [classes, selectedClassId]);

  useEffect(() => {
    const socket = new WebSocket(getChatWebSocketUrl());
    socketRef.current = socket;

    socket.addEventListener("open", () => {
      if (selectedClassIdRef.current !== "") {
        socket.send(JSON.stringify({
          type: "join_class",
          class_id: selectedClassIdRef.current,
        }));
      }
    });

    socket.addEventListener("message", (event) => {
      let data;

      try {
        data = JSON.parse(event.data);
      } catch {
        return;
      }

      if (data.type === "new_chat_message") {
        addLivePost(data.post);
      }
    });

    return () => {
      socket.close();
      socketRef.current = null;
    };
  }, []);

  useEffect(() => {
    const socket = socketRef.current;

    if (selectedClassId === "" || socket === null || socket.readyState !== WebSocket.OPEN) {
      return;
    }

    socket.send(JSON.stringify({
      type: "join_class",
      class_id: selectedClassId,
    }));
  }, [selectedClassId]);

  const messages = posts
    .filter((post) => String(post.class_id) === selectedClassId)
    .slice()
    .sort((a, b) => new Date(a.created_at) - new Date(b.created_at));

  useEffect(() => {
    if (messagesRef.current === null) {
      return;
    }

    if (lastClassRef.current !== selectedClassId || atBottom) {
      scrollToBottom();
      setAtBottom(true);
    }

    lastClassRef.current = selectedClassId;
  }, [messages.length, selectedClassId]);

  function scrollToBottom() {
    messagesRef.current.scrollTop = messagesRef.current.scrollHeight;
    setAtBottom(true);
  }

  function checkScroll() {
    const messageBox = messagesRef.current;
    const distanceFromBottom = messageBox.scrollHeight - messageBox.scrollTop - messageBox.clientHeight;

    setAtBottom(distanceFromBottom < 20);
  }

  async function sendMessage(event) {
    event.preventDefault();

    if (msg.trim() === "" || selectedClassId === "") {
      return;
    }

    const savedPost = await addPost({
      title: "Message",
      category: selectedPostType,
      class_id: selectedClassId,
      body: msg.trim(),
      isAnonymous: false,
      shareWithDojo: false,
    });

    if (savedPost === null) {
      return;
    }

    if (socketRef.current?.readyState === WebSocket.OPEN) {
      socketRef.current.send(JSON.stringify({
        type: "chat_message",
        class_id: selectedClassId,
        post: savedPost,
      }));
    }

    setMsg("");
  }

  function handleKeyDown(event) {
    if (event.key === "Enter" && !event.shiftKey) {
      sendMessage(event);
    }
  }

  return (
    <main className="chat-layout">
      <section className="chat-panel">
        <MobileClassFilter
          classes={classes}
          selectedClassId={selectedClassId}
          setSelectedClassId={setSelectedClassId}
          showAll={false}
        />

        <div className="chat-messages-wrap">
          <div
            className="chat-messages"
            ref={messagesRef}
            onScroll={checkScroll}
          >
            {classes.length === 0 ? (
              <p className="text-muted">Join a class to start chatting.</p>
            ) : messages.map((post) => {
              const isMine = post.author_email === currentUserEmail;

              return (
                <div
                  className={isMine ? "chat-row mine" : "chat-row"}
                  key={post.post_id}
                >
                  <div className={isMine ? "chat-bubble mine" : "chat-bubble"}>
                    {!isMine && (
                      <p className="chat-sender">{post.display_author}</p>
                    )}
                    <p>{post.body}</p>
                  </div>
                </div>
              );
            })}
          </div>

          {!atBottom && (
            <button
              type="button"
              className="jump-latest-button"
              onClick={scrollToBottom}
            >
              Jump to latest
            </button>
          )}
        </div>

        <form className="chat-box" onSubmit={sendMessage}>
          <textarea
            value={msg}
            onChange={(event) => setMsg(event.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="Message..."
          ></textarea>

          <button type="submit" className="btn btn-primary">
            Send
          </button>
        </form>
      </section>

      <aside className="post-side-panel">
        <ClassFilter
          classes={classes}
          selectedClassId={selectedClassId}
          setSelectedClassId={setSelectedClassId}
          showAll={false}
        />
      </aside>
    </main>
  );
}

export default ChatLayout;
