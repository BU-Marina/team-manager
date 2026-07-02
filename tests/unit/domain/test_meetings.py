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


@pytest.mark.unit
@pytest.mark.meetings
class TestMeetingOverlap:
    @pytest.mark.parametrize(
        "start1, end1, start2, end2, expected_conflict",
        [
            # Полное перекрытие (вторая встреча внутри первой)
            (0, 10, 2, 5, True),
            # Полное перекрытие (первая внутри второй)
            (2, 5, 0, 10, True),
            # Стык в стык (конец первой = начало второй)
            (0, 5, 5, 10, False),
            # Не пересекаются (первая раньше)
            (0, 5, 7, 10, False),
            # Не пересекаются (вторая раньше)
            (7, 10, 0, 5, False),
            # Частичное перекрытие (начало первой внутри второй)
            (5, 10, 7, 12, True),
            # Частичное перекрытие (конец первой внутри второй)
            (0, 5, 3, 10, True),
            # Одинаковое время
            (0, 10, 0, 10, True),
            # Стык в стык (конец второй = начало первой)
            (5, 10, 0, 5, False),
        ],
    )
    def test_overlap_logic(self, start1, end1, start2, end2, expected_conflict):
        """Проверка логики пересечений: NOT (new_end <= existing_start OR new_start >= existing_end)"""
        base = datetime(2026, 1, 1, 0, 0, 0)
        existing_start = base + timedelta(hours=start1)
        existing_end = base + timedelta(hours=end1)
        new_start = base + timedelta(hours=start2)
        new_end = base + timedelta(hours=end2)

        # Логика: конфликт, если NOT (new_end <= existing_start OR new_start >= existing_end)
        has_conflict = not (new_end <= existing_start or new_start >= existing_end)
        assert has_conflict == expected_conflict
