"""Service for interacting with APS Model Coordination problems."""
from __future__ import annotations

from datetime import datetime
from typing import List, Optional
from urllib.parse import quote

import httpx

from app.core.config import settings
from app.core.logging import get_logger, log_api_call
from app.models.problem import (
    Problem,
    ProblemCreatePayload,
    ProblemLinkPayload,
    ProblemPriority,
    ProblemReference,
    ProblemStatus,
)
from app.mock.problems import get_mock_problems
from app.services.aps_auth import APSAuthClient, get_auth_client

logger = get_logger(__name__)


class ProblemsService:
    """Business logic for fetching and managing problems."""

    def __init__(self, auth_client: Optional[APSAuthClient] = None):
        self._auth_client = auth_client or get_auth_client()
        self._base_url = f"{settings.aps_base_url}/modelcoordination/v1"
        coordination_space = settings.aps_coordination_space_id
        if coordination_space:
            if coordination_space.lower().startswith("urn:"):
                self._container_id = quote(coordination_space, safe="")
            else:
                self._container_id = coordination_space
        else:
            self._container_id = settings.aps_project_id

    async def _get_headers(self) -> dict[str, str]:
        """Return headers with APS access token."""
        token = await self._auth_client.get_token()
        return {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        }

    def _map_problem(self, raw: dict) -> Problem:
        """Convert raw APS data to internal model."""
        attributes = raw.get("attributes", raw)
        relationships = raw.get("relationships", {})

        status_value = attributes.get("status", "open")
        priority_value = attributes.get("priority", "medium")

        references: List[ProblemReference] = []
        clash_ids: List[str] = []

        refs = relationships.get("references", {}).get("data", [])
        for ref in refs:
            ref_type = ref.get("type") or ref.get("attributes", {}).get("type")
            ref_id = ref.get("id") or ref.get("attributes", {}).get("id")
            title = ref.get("attributes", {}).get("title")
            urn = ref.get("attributes", {}).get("urn")

            reference = ProblemReference(type=ref_type or "unknown", id=ref_id or "", title=title, urn=urn)
            references.append(reference)

            if (ref_type or "").lower() == "clash" and ref_id:
                clash_ids.append(ref_id)

        created_raw = attributes.get("created_at") or attributes.get("createdAt")
        updated_raw = attributes.get("updated_at") or attributes.get("updatedAt")

        def parse_dt(value: Optional[str]) -> Optional[datetime]:
            if not value:
                return None
            try:
                return datetime.fromisoformat(value.replace("Z", "+00:00"))
            except ValueError:
                return None

        created_at = parse_dt(created_raw) or datetime.utcnow()
        updated_at = parse_dt(updated_raw) or created_at

        status_enum = (
            ProblemStatus(status_value)
            if status_value in ProblemStatus._value2member_map_
            else ProblemStatus.OPEN
        )
        priority_enum = (
            ProblemPriority(priority_value)
            if priority_value in ProblemPriority._value2member_map_
            else ProblemPriority.MEDIUM
        )

        return Problem(
            id=raw.get("id") or attributes.get("id"),
            title=attributes.get("title", "Sans titre"),
            description=attributes.get("description"),
            status=status_enum,
            priority=priority_enum,
            assigned_to=attributes.get("assigned_to") or attributes.get("assignedTo"),
            due_date=parse_dt(attributes.get("due_date") or attributes.get("dueDate")),
            created_at=created_at,
            updated_at=updated_at,
            references=references,
            clash_ids=clash_ids,
        )

    async def get_problems(self, clash_id: Optional[str] = None) -> List[Problem]:
        """Retrieve problems from APS or mock store."""
        if settings.use_mock or not self._container_id:
            problems = get_mock_problems()
            if clash_id:
                problems = [p for p in problems if clash_id in p.clash_ids]
            return problems

        headers = await self._get_headers()
        params = {"include": "references"}
        url = f"{self._base_url}/containers/{self._container_id}/problems"
        log_api_call(logger, "GET", url, params=params)

        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.get(url, headers=headers, params=params)
                response.raise_for_status()
                payload = response.json()
        except httpx.HTTPStatusError as exc:
            status_code = exc.response.status_code if exc.response else None
            logger.error(f"Failed to retrieve problems from APS: {exc}")
            if status_code in (401, 403, 404):
                logger.warning("APS problems unavailable (status %s) – using mock data.", status_code)
                problems = get_mock_problems()
                if clash_id:
                    problems = [p for p in problems if clash_id in p.clash_ids]
                return problems
            raise
        except httpx.HTTPError as exc:
            logger.error(f"HTTP error retrieving problems: {exc}")
            raise

        raw_items = (
            payload.get("data")
            or payload.get("results")
            or payload.get("items")
            or payload.get("problems")
            or []
        )

        problems = [self._map_problem(item) for item in raw_items]

        if clash_id:
            problems = [problem for problem in problems if clash_id in problem.clash_ids]
        return problems

    def _link_problem_mock(self, problem_id: str, clash_id: str) -> Problem:
        problems = get_mock_problems()
        target = next((p for p in problems if p.id == problem_id), None)
        if not target:
            raise ValueError(f"Problem {problem_id} not found")
        if clash_id not in target.clash_ids:
            target.clash_ids.append(clash_id)
            target.references.append(ProblemReference(type="clash", id=clash_id))
        return target

    def _unlink_problem_mock(self, problem_id: str, clash_id: str) -> Problem:
        problems = get_mock_problems()
        target = next((p for p in problems if p.id == problem_id), None)
        if not target:
            raise ValueError(f"Problem {problem_id} not found")
        target.clash_ids = [cid for cid in target.clash_ids if cid != clash_id]
        target.references = [ref for ref in target.references if ref.id != clash_id]
        return target

    async def create_problem(self, payload: ProblemCreatePayload) -> Problem:
        """Create a new problem and optionally link it to a clash."""
        if settings.use_mock or not self._container_id:
            problems = get_mock_problems()
            problem = Problem(
                id=f"problem-{len(problems) + 1:04d}",
                title=payload.title,
                description=payload.description,
                status=payload.status,
                priority=payload.priority,
                assigned_to=payload.assigned_to,
                due_date=payload.due_date,
                references=[ProblemReference(type="clash", id=payload.clash_id, title=payload.title)],
                clash_ids=[payload.clash_id],
            )
            problems.append(problem)
            return problem

        headers = await self._get_headers()
        url = f"{self._base_url}/containers/{self._container_id}/problems"

        body = {
            "title": payload.title,
            "description": payload.description,
            "status": payload.status.value,
            "priority": payload.priority.value,
            "references": [
                {
                    "type": "clash",
                    "id": payload.clash_id,
                }
            ],
        }

        if payload.assigned_to:
            body["assigned_to"] = payload.assigned_to
        if payload.due_date:
            body["due_date"] = payload.due_date.isoformat()

        log_api_call(logger, "POST", url)

        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(url, headers=headers, json=body)
            response.raise_for_status()
            raw_problem = response.json().get("data") or response.json()

        return self._map_problem(raw_problem)

    async def link_problem(self, problem_id: str, payload: ProblemLinkPayload) -> Problem:
        """Link an existing problem to a clash."""
        if settings.use_mock or not self._container_id:
            return self._link_problem_mock(problem_id, payload.clash_id)

        headers = await self._get_headers()
        url = f"{self._base_url}/containers/{self._container_id}/problems/{problem_id}/references"
        body = {"type": "clash", "id": payload.clash_id}

        log_api_call(logger, "POST", url, body=body)

        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(url, headers=headers, json=body)
                response.raise_for_status()
        except httpx.HTTPStatusError as exc:
            status_code = exc.response.status_code if exc.response else None
            logger.error(f"Failed to link problem {problem_id}: {exc}")
            if status_code in (401, 403, 404):
                logger.warning("Falling back to mock link operation (status %s).", status_code)
                return self._link_problem_mock(problem_id, payload.clash_id)
            raise
        except httpx.HTTPError as exc:
            logger.error(f"HTTP error linking problem {problem_id}: {exc}")
            raise

        problems = await self.get_problems()
        problem = next((item for item in problems if item.id == problem_id), None)
        if not problem:
            raise ValueError(f"Problem {problem_id} not found after linking")
        return problem

    async def unlink_problem(self, problem_id: str, payload: ProblemLinkPayload) -> Problem:
        """Remove clash link from a problem."""
        if settings.use_mock or not self._container_id:
            return self._unlink_problem_mock(problem_id, payload.clash_id)

        headers = await self._get_headers()
        url = f"{self._base_url}/containers/{self._container_id}/problems/{problem_id}/references/{payload.clash_id}"

        log_api_call(logger, "DELETE", url)

        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.delete(url, headers=headers)
                response.raise_for_status()
        except httpx.HTTPStatusError as exc:
            status_code = exc.response.status_code if exc.response else None
            logger.error(f"Failed to unlink problem {problem_id}: {exc}")
            if status_code in (401, 403, 404):
                logger.warning("Falling back to mock unlink operation (status %s).", status_code)
                return self._unlink_problem_mock(problem_id, payload.clash_id)
            raise
        except httpx.HTTPError as exc:
            logger.error(f"HTTP error unlinking problem {problem_id}: {exc}")
            raise

        problems = await self.get_problems()
        problem = next((item for item in problems if item.id == problem_id), None)
        if not problem:
            raise ValueError(f"Problem {problem_id} not found after unlinking")
        return problem


_problems_service: Optional[ProblemsService] = None


def get_problems_service() -> ProblemsService:
    """Return singleton instance of ProblemsService."""
    global _problems_service
    if _problems_service is None:
        _problems_service = ProblemsService()
    return _problems_service
