import { useState } from "react";

function PostView({ postData, onBack }) {

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
      <p className="text-muted mb-2">
        Type: {postData.category} | Class: {postData.class_id}
      </p>

      <div className="post-view-body">{postData.body}</div>

    </div>
  );
}

export default PostView;
