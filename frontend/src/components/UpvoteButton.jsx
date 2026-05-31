function UpvoteButton({ post, onVote }) {
  const buttonClass = post.has_upvoted
    ? "upvote-button upvoted"
    : "upvote-button";

  async function clickVote(event) {
    event.stopPropagation(); // prevent post from also opening!
    await onVote(post.post_id);
  }

  return (
    <button
      type="button"
      className={buttonClass}
      onClick={clickVote}
    >
      ▲ {post.upvotes}
    </button>
  );
}

export default UpvoteButton;
