import { useEffect, useState } from "react";
import Followup, { FollowupForm } from "./Followup";
import UpvoteButton from "./UpvoteButton";

const emptyFollowups = {
  answers: [],
  teacher_responses: [],
  other: [],
};

function PostView({ postData, onBack, showClass, onVote, onDelete }) {
  const [followups, setFollowups] = useState(emptyFollowups);

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

    setFollowups((old) => ({
      ...old,
      other: [...old.other, data.followup],
    }));
  }

  async function voteFollowup(postId) {
    const post = await onVote(postId);
    setFollowups((old) => updateGroups(old, postId, post));
    return post;
  }

  async function deleteFollowup(postId) {
    const deleted = await onDelete(postId);
    if (deleted) {
      setFollowups((old) => removeFromGroups(old, postId));
    }
  }

  function showGroup(title, group) {
    if (group.length === 0) {
      return null;
    }

    return (
      <div className="followup-group">
        <h4>{title}</h4>

        {group.map((followup) => (
          <Followup
            key={followup.post_id}
            followup={followup}
            onVote={voteFollowup}
            onDelete={deleteFollowup}
          />
        ))}
      </div>
    );
  }

  const followupCount =
    followups.answers.length +
    followups.teacher_responses.length +
    followups.other.length;

  function deletePost() {
    if (confirm("Delete this post?")) {
      onDelete(postData.post_id);
    }
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

      <div className="post-view-actions">
        <UpvoteButton post={postData} onVote={onVote} />

        {postData.can_delete && (
          <button
            type="button"
            className="post-delete-button"
            onClick={deletePost}
          >
            Delete
          </button>
        )}
      </div>

      <section className="followups">
        <h3>Followups</h3>

        <FollowupForm
          onSubmit={addFollowup}
          placeholder="Write a followup..."
        />

        {followupCount === 0 ? (
          <p className="text-muted">No followups yet.</p>
        ) : (
          <>
            {showGroup("Answers", followups.answers)}
            {showGroup("Teacher Responses", followups.teacher_responses)}
            {showGroup("Other Followups", followups.other)}
          </>
        )}
      </section>
    </div>
  );
}

function updateGroups(groups, postId, post) {
  return {
    answers: updateList(groups.answers, postId, post),
    teacher_responses: updateList(groups.teacher_responses, postId, post),
    other: updateList(groups.other, postId, post),
  };
}

function updateList(followups, postId, post) {
  return followups.map((followup) => (
    followup.post_id === postId ? post : followup
  ));
}

function removeFromGroups(groups, postId) {
  return {
    answers: removeFromList(groups.answers, postId),
    teacher_responses: removeFromList(groups.teacher_responses, postId),
    other: removeFromList(groups.other, postId),
  };
}

function removeFromList(followups, postId) {
  return followups.filter((followup) => followup.post_id !== postId);
}

export default PostView;
