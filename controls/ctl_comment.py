


from fastapi import APIRouter, Depends, HTTPException

from db.db_server import DataBaseServer
from models.comment import Comment, CommentIn
from utils.token import get_current_user_info


session = DataBaseServer().get_session()
comment_router = APIRouter(prefix="/comments", tags=["评论功能"])

#创建评论（权限：普通用户和管理员)
@comment_router.post("/create")
def create_comment(comment_in: CommentIn,
                   current_user_info: dict = Depends(get_current_user_info)):
    if current_user_info["role"] not in ["admin", "user"]:
        raise HTTPException(status_code=403, detail="无权限创建评论")
    new_comment = Comment(
        content=comment_in.content,
        song_id=comment_in.song_id,
        creater_id=current_user_info["user_id"]
    )
    session.add(new_comment)
    session.commit()
    return {"message": "评论创建成功", "comment_id": new_comment.id}

#删除评论（权限：管理员和评论创建者）
@comment_router.post("/delete/{comment_id}")
def delete_comment(comment_id: int,
                   current_user_info: dict = Depends(get_current_user_info)):
    comment = session.query(Comment).filter(Comment.id == comment_id).first()
    if not comment:
        raise HTTPException(status_code=404, detail="评论不存在")
    if comment.creater_id != current_user_info["user_id"] and current_user_info["role"] != "admin":
        raise HTTPException(status_code=403, detail="无权限删除该评论")
    session.delete(comment)
    session.commit()
    return {"message": "评论删除成功"}

#评论应不可修改

#查看某首歌曲下的所有评论，只显示评论id和评论时间（权限：所有用户）
#按照创建时间排序，最新的评论在前面
@comment_router.post("/view_all/{song_id}")
def view_comments(song_id: int):
    comments = session.query(Comment).filter(Comment.song_id == song_id).order_by(Comment.created_at.desc()).all()
    return [{"comment_id": comment.id, "create_time": comment.create_time} for comment in comments]


#查看某条评论的详细信息（权限：所有用户）
@comment_router.post("/view/{comment_id}")
def view_comment_details(comment_id: int):
    comment = session.query(Comment).filter(Comment.id == comment_id).first()
    if not comment:
        raise HTTPException(status_code=404, detail="评论不存在")
    return {
        "comment_id": comment.id,
        "content": comment.content,
        "song_id": comment.song_id,
        "creater_id": comment.creater_id,
        "created_at": comment.created_at
    }