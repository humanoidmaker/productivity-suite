from __future__ import annotations
"""Comments API — add, reply, resolve, delete."""

import uuid
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.middleware.auth_middleware import CurrentUser, get_current_user
from app.models.comment import Comment
from app.models.user import User
from app.schemas.comment import CommentCreate, CommentUpdate, CommentResponse

router = APIRouter(prefix="/comments", tags=["comments"])


@router.post("", response_model=CommentResponse, status_code=status.HTTP_201_CREATED)
async def add_comment(body: CommentCreate, user: CurrentUser = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    comment = Comment(
        file_type=body.file_type, file_id=body.file_id, user_id=user.id,
        content=body.content, position_json=body.position_json, parent_comment_id=body.parent_comment_id,
    )
    db.add(comment)
    await db.flush()
    return await _enrich_comment(db, comment)


@router.get("/{file_type}/{file_id}", response_model=list[CommentResponse])
async def list_comments(file_type: str, file_id: uuid.UUID, user: CurrentUser = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Comment).where(Comment.file_type == file_type, Comment.file_id == file_id).order_by(Comment.created_at)
    )
    comments = result.scalars().all()
    return [await _enrich_comment(db, c) for c in comments]


@router.patch("/{comment_id}", response_model=CommentResponse)
async def update_comment(comment_id: uuid.UUID, body: CommentUpdate, user: CurrentUser = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Comment).where(Comment.id == comment_id))
    comment = result.scalar_one_or_none()
    if not comment or comment.user_id != user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Comment not found")
    comment.content = body.content
    await db.flush()
    return await _enrich_comment(db, comment)


@router.post("/{comment_id}/resolve", response_model=CommentResponse)
async def resolve_comment(comment_id: uuid.UUID, user: CurrentUser = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Comment).where(Comment.id == comment_id))
    comment = result.scalar_one_or_none()
    if not comment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Comment not found")
    comment.resolved = True
    comment.resolved_by = user.id
    comment.resolved_at = datetime.now(timezone.utc)
    await db.flush()
    return await _enrich_comment(db, comment)


@router.delete("/{comment_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_comment(comment_id: uuid.UUID, user: CurrentUser = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Comment).where(Comment.id == comment_id))
    comment = result.scalar_one_or_none()
    if not comment or comment.user_id != user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Comment not found")
    await db.delete(comment)
    await db.flush()


async def _enrich_comment(db: AsyncSession, comment: Comment) -> CommentResponse:
    result = await db.execute(select(User.name, User.avatar_url).where(User.id == comment.user_id))
    row = result.one_or_none()
    resp = CommentResponse.model_validate(comment)
    if row:
        resp.author_name = row[0]
        resp.author_avatar = row[1]
    return resp
