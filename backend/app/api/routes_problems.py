"""API endpoints for managing Model Coordination problems."""
from fastapi import APIRouter, HTTPException, Query

from app.models.problem import Problem, ProblemCreatePayload, ProblemLinkPayload, ProblemsResponse
from app.services.problems import get_problems_service

router = APIRouter(prefix="/api/problems", tags=["problems"])


@router.get("", response_model=ProblemsResponse)
async def list_problems(clash_id: str | None = Query(default=None)):
    """
    Retrieve problems from APS.

    Optionally filter by a specific clash identifier.
    """
    service = get_problems_service()
    problems = await service.get_problems(clash_id=clash_id)
    return ProblemsResponse(problems=problems, total=len(problems))


@router.post("", response_model=Problem, status_code=201)
async def create_problem(payload: ProblemCreatePayload):
    """
    Create a new problem and link it to the provided clash identifier.

    Requires Autodesk ACC permissions to create issues. The backend uses the
    APS Model Coordination Problems API:
    https://aps.autodesk.com/en/docs/model-coordination/v1/reference/http/problems-POST/
    """
    service = get_problems_service()
    try:
        return await service.create_problem(payload)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Failed to create problem: {exc}") from exc


@router.post("/{problem_id}/link", response_model=Problem)
async def link_problem(problem_id: str, payload: ProblemLinkPayload):
    """
    Attach an existing problem to an additional clash.

    Internally this calls POST /problems/{problem_id}/references with type "clash".
    """
    service = get_problems_service()
    try:
        problem = await service.link_problem(problem_id, payload)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Failed to link problem: {exc}") from exc

    if not problem:
        raise HTTPException(status_code=404, detail=f"Problem {problem_id} not found")
    return problem


@router.delete("/{problem_id}/link", response_model=Problem)
async def unlink_problem(problem_id: str, payload: ProblemLinkPayload):
    """
    Remove clash link from the problem.

    Internally this calls DELETE /problems/{problem_id}/references/{clash_id}.
    """
    service = get_problems_service()
    try:
        problem = await service.unlink_problem(problem_id, payload)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Failed to unlink problem: {exc}") from exc

    if not problem:
        raise HTTPException(status_code=404, detail=f"Problem {problem_id} not found")
    return problem
