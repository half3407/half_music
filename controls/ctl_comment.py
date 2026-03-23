from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from deps.pagination import PaginationParams, get_pagination
from deps.database import get_db
from deps.permissions import get_comment_with_permission, require_authenticated
from models.comment import Comment, CommentIn

comment_router = APIRouter(prefix="/comments", tags=["评论功能"])

#创建评论（权限：普通用户和管理员)
@comment_router.post("/create")
def create_comment(comment_in: CommentIn,
                   user = Depends(require_authenticated),
                   db: Session = Depends(get_db)):
    new_comment = Comment(
        content=comment_in.content,
        song_id=comment_in.song_id,
        creater_id=user["user_id"]
    )
    db.add(new_comment)
    db.commit()
    return {"message": "评论创建成功", "comment_id": new_comment.id}

#删除评论（权限：管理员和评论创建者）
@comment_router.post("/delete/{comment_id}")
def delete_comment(comment: Comment = Depends(get_comment_with_permission),
                   db: Session = Depends(get_db)):
    db.delete(comment)
    db.commit()
    return {"message": "评论删除成功"}

#评论应不可修改

#查看某首歌曲下的所有评论，只显示评论id和评论时间（权限：所有用户）
@comment_router.post("/view_all/{song_id}")
def view_comments(song_id: int,
                  pagination: PaginationParams = Depends(get_pagination),
                   db: Session = Depends(get_db)):
    #按照创建时间排序，最新的评论在前面，分页查询，每页显示12条数据
    commens = db.query(Comment).filter(Comment.song_id == song_id).order_by(Comment.created_at.desc()).offset((pagination.page-1)*pagination.page_size).limit(pagination.page_size).all()
    result = []
    for comment in commens:
        result.append({
            "comment_id": comment.id,
            "created_at": comment.created_at
        })
    return result


#查看某条评论的详细信息（权限：所有用户）
@comment_router.post("/view/{comment_id}")
def view_comment_details(comment_id: int,
                         db: Session = Depends(get_db)):
    comment = db.query(Comment).filter(Comment.id == comment_id).first()
    if not comment:
        raise HTTPException(status_code=404, detail="评论不存在")
    return {
        "comment_id": comment.id,
        "content": comment.content,
        "song_id": comment.song_id,
        "creater_id": comment.creater_id,
        "created_at": comment.created_at
    }