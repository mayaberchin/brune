import { useEffect, useState } from "react";
import Followup, { FollowupForm } from "./Followup";

function PostView({ postData, onBack, showClass }) {
  const [followups, setFollowups] = useState([]);

  useEffect(() => {
    async function loadFollowups() {
      const response = await fetch(`/api/posts/${postData.post_id}/followups`);
      const data = await response.json();
      setFollowups(data.followups);
    }

    loadFollowups();
  }, [postData.post_id]);

  async function addFollowup(body, isAnonymous) {
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

        <FollowupForm
          onSubmit={addFollowup}
          placeholder="Write a followup..."
        />

        {followups.length === 0 ? (
          <p className="text-muted">No followups yet.</p>
        ) : (
          followups.map((followup) => (
            <Followup key={followup.post_id} followup={followup} />
          ))
        )}
      </section>
    </div>
  );
}

export default PostView;
