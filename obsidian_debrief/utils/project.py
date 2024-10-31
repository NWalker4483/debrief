import re
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional

import obsidiantools.api as otools
from pydantic import BaseModel, Field


class TaskPriority(str, Enum):
    HIGHEST = "⏫"
    HIGH = "🔼"
    MEDIUM = "🔽"
    LOW = "⏬"

class Task(BaseModel):
    content: str
    completed: bool = False
    priority: Optional[TaskPriority] = None
    due_date: Optional[datetime] = None
    completion_date: Optional[datetime] = None
    tags: List[str] = Field(default_factory=list)

    class Config:
        use_enum_values = True

class ObsidianFile(BaseModel):
    name: str
    path: Path
    content: str
    tasks: List[Task] = Field(default_factory=list)
    tags: List[str] = Field(default_factory=list)
    front_matter: Dict = Field(default_factory=dict)
    backlinks: List[str] = Field(default_factory=list)
    wikilinks: List[str] = Field(default_factory=list)

    class Config:
        arbitrary_types_allowed = True

class Project(BaseModel):
    main_file: ObsidianFile
    working_files: List[ObsidianFile] = Field(default_factory=list)
    status: str = Field(default="active")
    priority: Optional[TaskPriority] = None
    start_date: Optional[datetime] = None
    due_date: Optional[datetime] = None

    class Config:
        arbitrary_types_allowed = True

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

def parse_task_line(task_line: str) -> Optional[Task]:
    CHECKBOX_PATTERN = r"- \[([ xX])\]"
    PRIORITY_PATTERN = r"(⏫|🔼|🔽|⏬)"
    DATE_PATTERN = r"📅 (\d{4}-\d{2}-\d{2})"
    COMPLETION_PATTERN = r"✅ (\d{4}-\d{2}-\d{2})"
    TAG_PATTERN = r"#(\w+)"

    checkbox_match = re.search(CHECKBOX_PATTERN, task_line)
    if not checkbox_match:
        return None

    completed = checkbox_match.group(1).lower() == "x"
    content = task_line[checkbox_match.end():].strip()

    priority = None
    priority_match = re.search(PRIORITY_PATTERN, content)
    if priority_match:
        priority = priority_match.group(1)
        content = content.replace(priority_match.group(1), "").strip()

    due_date = None
    completion_date = None

    due_match = re.search(DATE_PATTERN, content)
    if due_match:
        due_date = datetime.strptime(due_match.group(1), "%Y-%m-%d")
        content = content.replace(f"📅 {due_match.group(1)}", "").strip()

    complete_match = re.search(COMPLETION_PATTERN, content)
    if complete_match:
        completion_date = datetime.strptime(complete_match.group(1), "%Y-%m-%d")
        content = content.replace(f"✅ {complete_match.group(1)}", "").strip()

    tags = re.findall(TAG_PATTERN, content)
    for tag in tags:
        content = content.replace(f"#{tag}", "").strip()

    return Task(
        content=content,
        completed=completed,
        priority=priority,
        due_date=due_date,
        completion_date=completion_date,
        tags=tags
    )

class ProjectLoader:
    def __init__(self, vault_path: str):
        self.vault_path = Path(vault_path).resolve()
        if not self.vault_path.exists():
            raise ValueError(f"Vault path does not exist: {self.vault_path}")
        
        self.vault = otools.Vault(str(self.vault_path)).connect().gather()
        
    def _resolve_file_path(self, filename: str) -> Path:
        """Resolve the actual file path from the vault index"""
        relative_path = self.vault.md_file_index[filename]
        if Path(relative_path).is_absolute():
            return Path(relative_path)
        return (self.vault_path / relative_path).resolve()

    def _read_file_content(self, file_path: Path) -> str:
        """Read file content with proper encoding"""
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        return file_path.read_text(encoding='utf-8')

    def _load_file(self, filename: str) -> ObsidianFile:
        """Load a single file from the vault with proper path resolution"""
        file_path = self._resolve_file_path(filename)
        content = self._read_file_content(file_path)

        return ObsidianFile(
            name=filename,
            path=file_path,
            content=content,
            tasks=parse_file_tasks(content),
            tags=self.vault.get_tags(filename),
            front_matter=self.vault.get_front_matter(filename),
            backlinks=self.vault.get_backlinks(filename),
            wikilinks=self.vault.get_wikilinks(filename)
        )

    def load_project(self, main_file_name: str) -> Optional[Project]:
        """Load a project from its main file"""
        main_file = self._load_file(main_file_name)
        
        # Verify project tag exists
        if not any('project' in tag.lower() for tag in main_file.tags):
            return None

        # Load working files
        working_files = []
        for linked_file in main_file.backlinks:
            if linked_file in self.vault.md_file_index:
                working_file = self._load_file(linked_file)
                working_files.append(working_file)

        front_matter = main_file.front_matter
        return Project(
            main_file=main_file,
            working_files=working_files,
            status=front_matter.get('status', 'active'),
            priority=front_matter.get('priority'),
            start_date=front_matter.get('start_date'),
            due_date=front_matter.get('due_date')
        )

    def load_all_projects(self) -> List[Project]:
        """Load all projects from the vault"""
        projects = []
        for filename in self.vault.md_file_index:
            tags = self.vault.get_tags(filename)
            if any('project' in tag.lower() for tag in tags):
                project = self.load_project(filename)
                if project:
                    projects.append(project)
        return projects

def parse_file_tasks(content: str) -> List[Task]:
    """Parse all tasks from file content"""
    tasks = []
    for line in content.splitlines():
        task = parse_task_line(line.strip())
        if task:
            tasks.append(task)
    return tasks

if __name__ == "__main__":
    VAULT_PATH = "/home/walkenz1/Sync/HomeVault"
    
    # Initialize and validate vault path
    vault_path = Path(VAULT_PATH).resolve()
    print(f"Loading vault from: {vault_path}")
    
    loader = ProjectLoader(VAULT_PATH)
    
    # Display available files before processing
    print("\nAvailable files in vault:")
    for filename, filepath in loader.vault.md_file_index.items():
        print(f"- {filename}: {filepath}")
    
    # Load and display projects
    projects = loader.load_all_projects()
    
    print(f"\nFound {len(projects)} projects:")
    for project in projects:
        print(f"\nProject: {project.main_file.name}")
        print(f"Status: {project.status}")
        print(f"Priority: {project.priority}")
        print(f"Total tasks: {len(project.all_tasks)}")
        print(f"Pending tasks: {len(project.pending_tasks)}")
        print(f"Completed tasks: {len(project.completed_tasks)}")

        print("\nPending Tasks:")
        for task in project.pending_tasks:
            print(f"- {task.content}")
            if task.due_date:
                print(f"  Due: {task.due_date.strftime('%Y-%m-%d')}")
            if task.priority:
                print(f"  Priority: {task.priority}")

        print("\nWorking Files:")
        for file in project.working_files:
            print(f"- {file.name} ({len(file.tasks)} tasks)")

        print("-" * 80)