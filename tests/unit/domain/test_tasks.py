import pytest
from src.domain.tasks.entities import Task, Comment
from src.domain.tasks.value_objects import TaskStatus


@pytest.mark.unit
@pytest.mark.tasks
class TestTask:
    def test_create_task(self):
        task = Task.create(
            title="Test Task",
            description="Description",
            assignee_id=2,
            creator_id=1,
            team_id=1,
        )
        assert task.title == "Test Task"
        assert task.status == TaskStatus.OPEN

    def test_create_task_empty_title_fails(self):
        with pytest.raises(ValueError):
            Task.create(
                title=" ", description="Desc", assignee_id=2, creator_id=1, team_id=1
            )

    def test_start_task(self):
        task = Task.create(
            title="Task", description="Desc", assignee_id=2, creator_id=1, team_id=1
        )
        task.start()
        assert task.status == TaskStatus.IN_PROGRESS

    def test_start_already_in_progress_fails(self):
        task = Task.create(
            title="Task", description="Desc", assignee_id=2, creator_id=1, team_id=1
        )
        task.start()
        with pytest.raises(ValueError):
            task.start()

    def test_complete_task(self):
        task = Task.create(
            title="Task", description="Desc", assignee_id=2, creator_id=1, team_id=1
        )
        task.start()
        task.complete()
        assert task.status == TaskStatus.DONE

    def test_complete_not_started_fails(self):
        task = Task.create(
            title="Task", description="Desc", assignee_id=2, creator_id=1, team_id=1
        )
        with pytest.raises(ValueError):
            task.complete()


@pytest.mark.unit
@pytest.mark.tasks
class TestComments:
    def test_create_comment(self):
        comment = Comment.create(task_id=1, author_id=2, text="Good job")
        assert comment.text == "Good job"

    def test_create_empty_comment_fails(self):
        with pytest.raises(ValueError):
            Comment.create(task_id=1, author_id=2, text=" ")
