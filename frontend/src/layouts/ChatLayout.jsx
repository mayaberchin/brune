import { useState } from "react";

function ChatLayout({
  classes,
  posts,
  selectedPostType,
  currentUserEmail,
  addPost,
}) {
  const [selectedClassId, setSelectedClassId] = useState(String(classes[0].class_id));
  const [msg, setMsg] = useState("");

  const messages = posts
    .filter((post) => String(post.class_id) === selectedClassId)
    .slice()
    .reverse();

  async function sendMessage(event) {
    event.preventDefault();

    if (msg.trim() === "") {
      return;
    }

    await addPost({
      title: "Message",
      category: selectedPostType,
      class_id: selectedClassId,
      body: msg.trim(),
      isAnonymous: false,
      shareWithDojo: false,
    });
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
        <div className="chat-messages">
          {messages.map((post) => {
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
        <div className="class-filter-panel">
          <h2 className="h4">Courses</h2>

          {classes.map((classInfo) => (
            <button
              key={classInfo.class_id}
              type="button"
              className={
                selectedClassId === String(classInfo.class_id)
                  ? "class-filter active"
                  : "class-filter"
              }
              onClick={() => setSelectedClassId(String(classInfo.class_id))}
            >
              {classInfo.name}
            </button>
          ))}
        </div>
      </aside>
    </main>
  );
}

export default ChatLayout;
