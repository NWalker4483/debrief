from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import List, Optional
from enum import Enum
from datetime import datetime
import uvicorn

class TaskType(str, Enum):
    UPDATE = "update"
    CREATE = "create"
    COMPLETE = "complete"
    NEW = "new"

class TaskBase(BaseModel):
    content: str
    type: TaskType

class TaskCreate(TaskBase):
    pass

class Task(TaskBase):
    id: int
    created_at: datetime = Field(default_factory=datetime.now)


class DebirefUpdate(BaseModel):
    text: str
    project_tags: List[str] = Field(default_factory=list)
    vault_path: Optional[str] = None

class DebirefResponse(BaseModel):
    tasks: List[Task]
    summary: str
    processed_at: datetime = Field(default_factory=datetime.now)

class TaskBatchResponse(BaseModel):
    success: bool
    message: str
    processed_count: int

app = FastAPI(
    title="Debrief API",
    description="API for processing daily updates and managing tasks in Obsidian vault",
    version="1.0.0"
)

# In-memory storage for demo purposes
tasks_db = []
task_counter = 0

@app.post("/api/debrief", response_model=DebirefResponse)
async def process_debrief(update: DebirefUpdate):
    """
    Process a debrief update and generate suggested tasks.
    """
    global task_counter
    
    # Simulate AI processing of the debrief text
    # In a real implementation, this would:
    # 1. Process the text using an AI model
    # 2. Scan the vault for relevant files
    # 3. Generate appropriate suggestions
    
    # Generate mock tasks based on the update
    suggested_tasks = [
        Task(
            id=task_counter + 1,
            content=f"Update documentation for {update.project_tags[0]}",
            type=TaskType.UPDATE
        ),
        Task(
            id=task_counter + 2,
            content="Create new working file: meeting-notes.md",
            type=TaskType.CREATE
        ),
        Task(
            id=task_counter + 3,
            content="Mark task 'Review PR' as completed",
            type=TaskType.COMPLETE
        )
    ]
    
    # Update task counter
    task_counter += len(suggested_tasks)
    
    # Store tasks in memory
    tasks_db.extend(suggested_tasks)
    
    return DebirefResponse(
        tasks=suggested_tasks,
        summary=f"Processed update with {len(suggested_tasks)} suggestions",
        processed_at=datetime.now()
    )

@app.get("/api/tasks", response_model=List[Task])
async def get_tasks():
    """
    Retrieve all pending tasks.
    """
    return tasks_db

@app.delete("/api/tasks/{task_id}")
async def delete_task(task_id: int):
    """
    Delete a specific task by ID.
    """
    global tasks_db
    original_length = len(tasks_db)
    tasks_db = [task for task in tasks_db if task.id != task_id]
    
    if len(tasks_db) == original_length:
        raise HTTPException(status_code=404, detail="Task not found")
    
    return {"success": True, "message": "Task deleted"}

@app.post("/api/tasks/{task_id}/confirm")
async def confirm_task(task_id: int):
    """
    Confirm and process a specific task.
    """
    task = next((task for task in tasks_db if task.id == task_id), None)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    # Process the task based on its type
    # In a real implementation, this would:
    # 1. Create new files for CREATE tasks
    # 2. Update existing files for UPDATE tasks
    # 3. Mark tasks as complete for COMPLETE tasks
    # 4. Add new tasks for NEW tasks
    
    # Remove the task after processing
    tasks_db.remove(task)
    
    return {"success": True, "message": f"Task processed: {task.content}"}

@app.post("/api/tasks/confirm-all", response_model=TaskBatchResponse)
async def confirm_all_tasks():
    """
    Confirm and process all pending tasks.
    """
    global tasks_db
    task_count = len(tasks_db)
    
    if task_count == 0:
        return TaskBatchResponse(
            success=True,
            message="No tasks to process",
            processed_count=0
        )
    
    # Process all tasks
    # In a real implementation, this would process each task based on its type
    
    # Clear all tasks
    tasks_db = []
    
    return TaskBatchResponse(
        success=True,
        message=f"Processed {task_count} tasks",
        processed_count=task_count
    )

@app.delete("/api/tasks/clear-all", response_model=TaskBatchResponse)
async def clear_all_tasks():
    """
    Clear all pending tasks without processing them.
    """
    global tasks_db
    task_count = len(tasks_db)
    tasks_db = []
    
    return TaskBatchResponse(
        success=True,
        message=f"Cleared {task_count} tasks",
        processed_count=task_count
    )

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)