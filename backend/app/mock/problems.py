"""Mock data for problems when running in mock mode."""
from __future__ import annotations

from datetime import datetime, timedelta
from typing import List

from app.models.problem import Problem, ProblemPriority, ProblemReference, ProblemStatus

_MOCK_PROBLEMS: List[Problem] = []


def _build_mock_data() -> List[Problem]:
    now = datetime.utcnow()
    problems = [
        Problem(
            id="problem-0001",
            title="Collision gaine CVC / poutre",
            description="Vérifier le passage de la gaine CVC et ajuster l'ouverture dans la poutre.",
            status=ProblemStatus.OPEN,
            priority=ProblemPriority.HIGH,
            created_at=now - timedelta(days=5),
            updated_at=now - timedelta(days=1),
            references=[
                ProblemReference(type="clash", id="clash_00001", title="Clash #1"),
            ],
            clash_ids=["clash_00001"],
        ),
        Problem(
            id="problem-0002",
            title="Clash MEP / Structure niveau 3",
            description="Coordination nécessaire avant coulage de la dalle.",
            status=ProblemStatus.IN_PROGRESS,
            priority=ProblemPriority.MEDIUM,
            created_at=now - timedelta(days=10),
            updated_at=now - timedelta(days=2),
            references=[
                ProblemReference(type="clash", id="clash_00015", title="Clash #15"),
            ],
            clash_ids=["clash_00015"],
        ),
    ]
    return problems


def get_mock_problems(regenerate: bool = False) -> List[Problem]:
    """Return mock problems, regenerating when needed."""
    global _MOCK_PROBLEMS
    if regenerate or not _MOCK_PROBLEMS:
        _MOCK_PROBLEMS = _build_mock_data()
    return _MOCK_PROBLEMS
