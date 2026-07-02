import pytest
from datetime import datetime, timedelta
from src.domain.meetings.entities import Meeting


@pytest.mark.unit
@pytest.mark.meetings
class TestMeeting:
    def test_create_meeting(self):
        now = datetime.now()
        meeting = Meeting.create(
            title="Sprint Review",
            organizer_id=1,
            team_id=1,
            start_time=now,
            end_time=now + timedelta(hours=1),
        )
        assert meeting.title == "Sprint Review"

    def test_create_meeting_empty_title_fails(self):
        now = datetime.now()
        with pytest.raises(ValueError):
            Meeting.create(
                title=" ",
                organizer_id=1,
                team_id=1,
                start_time=now,
                end_time=now + timedelta(hours=1),
            )

    def test_create_meeting_invalid_times_fails(self):
        now = datetime.now()
        with pytest.raises(ValueError):
            Meeting.create(
                title="Test",
                organizer_id=1,
                team_id=1,
                start_time=now + timedelta(hours=1),
                end_time=now,
            )
