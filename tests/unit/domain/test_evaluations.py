import pytest
from src.domain.evaluations.entities import Evaluation


@pytest.mark.unit
@pytest.mark.evaluations
class TestEvaluation:
    def test_create_evaluation(self):
        evaluation = Evaluation.create(
            task_id=1, evaluator_id=2, score=4, comment="Good job"
        )
        assert evaluation.score == 4

    def test_create_evaluation_invalid_score_fails(self):
        with pytest.raises(ValueError, match="Оценка должна быть от 1 до 5"):
            Evaluation.create(task_id=1, evaluator_id=2, score=6)
