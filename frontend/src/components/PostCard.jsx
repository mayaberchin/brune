import { useState } from "react";

function PostCard({ postData }) {

  return (
    <div className="card mb-3">
      <div className="card-body">
        <div className="d-flex justify-content-between align-items-start gap-3">

          <div>
            <h5 className="mb-1">{postData.title}</h5>
            <p className="text-muted mb-2">
              Type: {postData.postType} | Class: {postData.classId}
            </p>

            <p className="mb-0">{postData.body}</p>

          </div>

        </div>
      </div>
    </div>
  );
}

export default PostCard;
