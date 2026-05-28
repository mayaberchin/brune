import { useState } from "react";

function PostPreview({ postData, onOpen, isSelected }) {
  const previewClassName = isSelected
    ? "post-preview selected"
    : "post-preview";

  return (
    <div className={previewClassName} onClick={() => onOpen(postData)}>
      <h2 className="post-preview-title">{postData.title}</h2>

      <p className="post-preview-meta">
        By {postData.display_author} | Type: {postData.category} | Class: {postData.class_id}
      </p>

      <p className="post-preview-body">{postData.body}</p>
    </div>
  );
}

export default PostPreview;
