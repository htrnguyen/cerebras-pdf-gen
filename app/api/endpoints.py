from fastapi import APIRouter, BackgroundTasks
from fastapi.responses import JSONResponse
from app.models.state import global_state
from app.core.workflow import DocumentGenerationWorkflow

router = APIRouter()


@router.post("/api/start")
def start_generation(data: dict, background_tasks: BackgroundTasks):
    if global_state.is_currently_running:
        return JSONResponse(
            {"status": "error", "message": "A generation process is already running."}
        )

    api_key = data.get("api_key")
    num_files = int(data.get("num_files", 1))

    if not (1 <= num_files <= 20):
        return JSONResponse(
            {
                "status": "error",
                "message": "File count must be between 1 and 20 to respect API rate limits.",
            }
        )

    if not api_key:
        return JSONResponse({"status": "error", "message": "API Key is required."})

    from app.services.ai_service import AIService
    if not AIService.verify_api_key(api_key):
        return JSONResponse({"status": "error", "message": "Mã API Key không hợp lệ hoặc đã hết hạn từ Cerebras Cloud."})

    background_tasks.add_task(DocumentGenerationWorkflow.run, api_key, num_files)
    return JSONResponse({"status": "success", "message": "Generation started."})


@router.get("/api/status")
def get_status():
    return JSONResponse(global_state.get_public_status())


@router.post("/api/reset")
def reset_status():
    if not global_state.is_currently_running:
        global_state.reset()
    return JSONResponse({"status": "success", "message": "State reset."})
