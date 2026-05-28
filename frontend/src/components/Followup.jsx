import { useEffect, useState } from "react";

function FollowupForm({ onSubmit, placeholder }) {
  const [body, setBody] = useState("");
  const [isAnonymous, setIsAnonymous] = useState(false);

  async function submitFollowup(event) {
    event.preventDefault();

    if (body.trim() === "") {
      return;
    }

    await onSubmit(body.trim(), isAnonymous);
    setBody("");
    setIsAnonymous(false);
  }

  return (
    <form className="followup-form" onSubmit={submitFollowup}>
      <textarea
        className="form-control"
        value={body}
        onChange={(event) => setBody(event.target.value)}
        placeholder={placeholder}
      ></textarea>

      <div className="followup-form-actions">
        <label className="form-check">
          <input
            type="checkbox"
            className="form-check-input"
            checked={isAnonymous}
            onChange={(event) => setIsAnonymous(event.target.checked)}
          />
          <span className="form-check-label">Post Anonymously</span>
        </label>

        <button type="submit" className="btn btn-primary btn-sm">
          Reply
        </button>
      </div>
    </form>
  );
}

function Followup({ followup, canReply = true }) {
  const [replies, setReplies] = useState([]);
  const [showReply, setShowReply] = useState(false);

  useEffect(() => {
    async function loadReplies() {
      const response = await fetch(`/api/posts/${followup.post_id}/followups`);
      const data = await response.json();
      setReplies(data.followups);
    }

    loadReplies();
  }, [followup.post_id]);

  async function addReply(body, isAnonymous) {
    const response = await fetch(`/api/posts/${followup.post_id}/followups`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        body: body,
        isAnonymous: isAnonymous,
      }),
    });
    const data = await response.json();

    if (!response.ok) {
      alert(data.error);
      return;
    }

    setReplies([...replies, data.followup]);
    setShowReply(false);
  }

  return (
    <div className="followup">
      <p className="followup-meta">By {followup.display_author}</p>
      <p className="followup-body">{followup.body}</p>

      {canReply && (
        <button
          type="button"
          className="btn btn-outline-primary btn-sm mt-2"
          onClick={() => setShowReply(!showReply)}
        >
          Reply
        </button>
      )}

      {showReply && canReply && (
        <FollowupForm
          onSubmit={addReply}
          placeholder="Reply to this followup..."
        />
      )}

      {replies.length > 0 && (
        <div className="followup-replies">
          {replies.map((reply) => (
            <Followup key={reply.post_id} followup={reply} canReply={false} />
          ))}
        </div>
      )}
    </div>
  );
}

export { FollowupForm };
export default Followup;
