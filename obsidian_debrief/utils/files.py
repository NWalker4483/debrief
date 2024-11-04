from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

from pydantic import BaseModel, Field

from obsidian_debrief.utils.project import Task, TaskPriority


class ObsidianFile(BaseModel):
    name: str
    path: Path
    content: str
    tasks: List[Task] = Field(default_factory=list)
    tags: List[str] = Field(default_factory=list)
    front_matter: Dict = Field(default_factory=dict)
    backlinks: List[str] = Field(default_factory=list)
    wikilinks: List[str] = Field(default_factory=list)

class Project(BaseModel):
    main_file: ObsidianFile
    working_files: List[ObsidianFile] = Field(default_factory=list)
    status: str = Field(default="active")
    priority: Optional[TaskPriority] = []
    start_date: Optional[datetime] = None
    due_date: Optional[datetime] = None

    @property
    def all_tasks(self) -> List[Task]:
        tasks = self.main_file.tasks.copy()
        for file in self.working_files:
            tasks.extend(file.tasks)
        return tasks

    @property
    def pending_tasks(self) -> List[Task]:
        return [task for task in self.all_tasks if not task.completed]

    @property
    def completed_tasks(self) -> List[Task]:
        return [task for task in self.all_tasks if task.completed]
