import { useEffect, useState } from "react";

function PostView({ postData, onBack, showClass }) {
  const [followups, setFollowups] = useState([]);
  const [body, setBody] = useState("");
  const [isAnonymous, setIsAnonymous] = useState(false);

  useEffect(() => {
    async function loadFollowups() {
      const response = await fetch(`/api/posts/${postData.post_id}/followups`);
      const data = await response.json();
      setFollowups(data.followups);
    }

    loadFollowups();
  }, [postData.post_id]);

  async function addFollowup(event) {
    event.preventDefault();

    if (body.trim() === "") {
      return;
    }

    const response = await fetch(`/api/posts/${postData.post_id}/followups`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        body: body.trim(),
        isAnonymous: isAnonymous,
      }),
    });
    const data = await response.json();

    if (!response.ok) {
      alert(data.error);
      return;
    }

    setFollowups([...followups, data.followup]);
    setBody("");
    setIsAnonymous(false);
  }

  return (
    <div className="post-view">
      <button
        type="button"
        className="btn btn-outline-secondary btn-sm mb-3"
        onClick={onBack}
      >
        ← Back to posts
      </button>

      <h2 className="mb-2">{postData.title}</h2>

      <p className="post-view-meta">
        By {postData.display_author}
        {showClass && " | Class: " + postData.class_id}
      </p>

      <div className="post-view-body">{postData.body}</div>

      <section className="followups">
        <h3>Followups</h3>

        {followups.length === 0 ? (
          <p className="text-muted">No followups yet.</p>
        ) : (
          followups.map((followup) => (
            <div className="followup" key={followup.post_id}>
              <p className="followup-meta">By {followup.display_author}</p>
              <p className="followup-body">{followup.body}</p>
            </div>
          ))
        )}

        <form className="followup-form" onSubmit={addFollowup}>
          <textarea
            className="form-control"
            value={body}
            onChange={(event) => setBody(event.target.value)}
            placeholder="Write a followup..."
          ></textarea>

          <div className="form-check mt-2">
            <input
              id="followupAnonymous"
              type="checkbox"
              className="form-check-input"
              checked={isAnonymous}
              onChange={(event) => setIsAnonymous(event.target.checked)}
            />
            <label htmlFor="followupAnonymous" className="form-check-label">
              Post Anonymously
            </label>
          </div>

          <button type="submit" className="btn btn-primary btn-sm mt-2">
            Reply
          </button>
        </form>
      </section>
    </div>
  );
}

export default PostView;
