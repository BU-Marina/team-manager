from sqladmin import ModelView
from src.infra.database.models import (
    UserModel,
    TeamModel,
    TaskModel,
    CommentModel,
    EvaluationModel,
    MeetingModel,
)


class UserAdmin(ModelView, model=UserModel):
    column_list = [
        UserModel.id,
        UserModel.email,
        UserModel.role,
        UserModel.team_id,
        UserModel.created_at,
    ]
    column_searchable_list = [UserModel.email]
    column_sortable_list = [UserModel.id, UserModel.created_at]
    form_columns = [UserModel.email, UserModel.role, UserModel.team_id]
    can_create = True
    can_edit = True
    can_delete = True


class TeamAdmin(ModelView, model=TeamModel):
    column_list = [TeamModel.id, TeamModel.name, TeamModel.owner_id, TeamModel.code]


class TaskAdmin(ModelView, model=TaskModel):
    column_list = [TaskModel.id, TaskModel.title, TaskModel.status, TaskModel.team_id]


class CommentAdmin(ModelView, model=CommentModel):
    column_list = [CommentModel.id, CommentModel.task_id, CommentModel.author_id]


class EvaluationAdmin(ModelView, model=EvaluationModel):
    column_list = [EvaluationModel.id, EvaluationModel.task_id, EvaluationModel.score]


class MeetingAdmin(ModelView, model=MeetingModel):
    column_list = [
        MeetingModel.id,
        MeetingModel.title,
        MeetingModel.team_id,
        MeetingModel.start_time,
    ]
