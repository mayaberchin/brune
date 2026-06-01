import { useEffect, useState } from "react";
import UpvoteButton from "./UpvoteButton";

const emptyReplies = {
  answers: [],
  teacher_responses: [],
  other: [],
};

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

function Followup({ followup, canReply = true, onVote, onDelete }) {
  const [replies, setReplies] = useState(emptyReplies);
  const [showReply, setShowReply] = useState(false);
  const [shownFollowup, setShownFollowup] = useState(followup);

  useEffect(() => {
    setShownFollowup(followup);
  }, [followup]);

  useEffect(() => {
    async function loadReplies() {
      const response = await fetch(`/api/posts/${shownFollowup.post_id}/followups`);
      const data = await response.json();
      setReplies(data.followups);
    }

    loadReplies();
  }, [shownFollowup.post_id]);

  async function addReply(body, isAnonymous) {
    const response = await fetch(`/api/posts/${shownFollowup.post_id}/followups`, {
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

    setReplies((old) => ({
      ...old,
      other: [...old.other, data.followup],
    }));
    setShowReply(false);
  }

  async function vote(postId) {
    const post = await onVote(postId);

    if (post.post_id === shownFollowup.post_id) {
      setShownFollowup(post);
    }

    setReplies((old) => updateGroups(old, postId, post));

    return post;
  }

  async function deleteFollowup() {
    if (confirm("Delete this followup?")) {
      await onDelete(shownFollowup.post_id);
    }
  }

  async function deleteReply(postId) {
    const deleted = await onDelete(postId);
    if (deleted) {
      setReplies((old) => removeFromGroups(old, postId));
    }
  }

  function showReplies(title, group) {
    if (group.length === 0) {
      return null;
    }

    return (
      <div className="followup-group">
        <h4>{title}</h4>

        {group.map((reply) => (
          <Followup
            key={reply.post_id}
            followup={reply}
            canReply={false}
            onVote={vote}
            onDelete={deleteReply}
          />
        ))}
      </div>
    );
  }

  const replyCount =
    replies.answers.length +
    replies.teacher_responses.length +
    replies.other.length;

  return (
    <div className="followup">
      <p className="followup-meta">By {shownFollowup.display_author}</p>
      <p className="followup-body">{shownFollowup.body}</p>

      <div className="followup-actions">
        <UpvoteButton post={shownFollowup} onVote={vote} />

        {shownFollowup.can_delete && (
          <button
            type="button"
            className="post-delete-button"
            onClick={deleteFollowup}
          >
            Delete
          </button>
        )}

        {canReply && (
          <button
            type="button"
            className="btn btn-outline-primary btn-sm"
            onClick={() => setShowReply(!showReply)}
          >
            Reply
          </button>
        )}
      </div>

      {showReply && canReply && (
        <FollowupForm
          onSubmit={addReply}
          placeholder="Reply to this followup..."
        />
      )}

      {replyCount > 0 && (
        <div className="followup-replies">
          {showReplies("Answers", replies.answers)}
          {showReplies("Teacher Responses", replies.teacher_responses)}
          {showReplies("Other Replies", replies.other)}
        </div>
      )}
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

function updateList(replies, postId, post) {
  return replies.map((reply) => (
    reply.post_id === postId ? post : reply
  ));
}

function removeFromGroups(groups, postId) {
  return {
    answers: removeFromList(groups.answers, postId),
    teacher_responses: removeFromList(groups.teacher_responses, postId),
    other: removeFromList(groups.other, postId),
  };
}

function removeFromList(replies, postId) {
  return replies.filter((reply) => reply.post_id !== postId);
}

export { FollowupForm };
export default Followup;
