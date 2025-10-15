#!/usr/bin/env python3

"""
Script to change task descriptions in a LeRobot dataset.
Usage: python change_task_description.py <dataset_dir> <new_task> [--backup]

This script updates:
1. meta/episodes.jsonl - Updates the "tasks" field for each episode
2. meta/tasks.jsonl - Updates the "task" field for task definitions
"""

import sys
import json
import shutil
import argparse
import ast
from pathlib import Path
from typing import List, Union

def update_episodes_jsonl(episodes_file: Path, new_tasks: List[str], create_backup: bool = False):
    """Update task descriptions in episodes.jsonl"""
    
    # Read all episodes
    episodes = []
    with open(episodes_file, 'r') as f:
        for line in f:
            episode = json.loads(line.strip())
            # Update the tasks field (it's a list)
            episode['tasks'] = new_tasks
            episodes.append(episode)
    
    # Create backup if requested
    if create_backup:
        backup_file = episodes_file.with_suffix('.jsonl.backup')
        shutil.copy2(episodes_file, backup_file)
        print(f"Created backup: {backup_file}")
    
    # Write updated episodes
    with open(episodes_file, 'w') as f:
        for episode in episodes:
            f.write(json.dumps(episode) + '\n')
    
    print(f"Updated {len(episodes)} episodes in {episodes_file}")

def update_tasks_jsonl(tasks_file: Path, new_tasks: List[str], create_backup: bool = False):
    """Update task descriptions in tasks.jsonl"""
    
    # Read all tasks
    tasks = []
    with open(tasks_file, 'r') as f:
        for line in f:
            line = line.strip()
            if line:  # Skip empty lines
                task = json.loads(line)
                # Update the task field (use first task for individual task definitions)
                task['task'] = new_tasks[0] if new_tasks else ""
                tasks.append(task)
    
    # Create backup if requested
    if create_backup:
        backup_file = tasks_file.with_suffix('.jsonl.backup')
        shutil.copy2(tasks_file, backup_file)
        print(f"Created backup: {backup_file}")
    
    # Write updated tasks
    with open(tasks_file, 'w') as f:
        for task in tasks:
            f.write(json.dumps(task) + '\n')
    
    print(f"Updated {len(tasks)} tasks in {tasks_file}")

def parse_task_input(task_input: str) -> List[str]:
    """Parse task input which can be a single task, JSON list, or comma-separated list"""
    task_input = task_input.strip()
    
    # Try parsing as JSON list first
    if task_input.startswith('[') and task_input.endswith(']'):
        try:
            tasks = ast.literal_eval(task_input)
            if isinstance(tasks, list) and all(isinstance(t, str) for t in tasks):
                return tasks
        except (ValueError, SyntaxError):
            pass
    
    # Try parsing as comma-separated list
    if ',' in task_input:
        tasks = [task.strip() for task in task_input.split(',')]
        return [task for task in tasks if task]  # Remove empty strings
    
    # Single task
    return [task_input]

def change_task_description(dataset_dir: str, new_tasks: Union[str, List[str]], create_backup: bool = False):
    """Change task descriptions in the dataset"""
    
    dataset_path = Path(dataset_dir)
    
    if not dataset_path.exists():
        raise FileNotFoundError(f"Dataset directory not found: {dataset_path}")
    
    meta_dir = dataset_path / "meta"
    if not meta_dir.exists():
        raise FileNotFoundError(f"Meta directory not found: {meta_dir}")
    
    episodes_file = meta_dir / "episodes.jsonl"
    tasks_file = meta_dir / "tasks.jsonl"
    
    # Check files exist
    if not episodes_file.exists():
        raise FileNotFoundError(f"Episodes file not found: {episodes_file}")
    
    if not tasks_file.exists():
        raise FileNotFoundError(f"Tasks file not found: {tasks_file}")
    
    print(f"Dataset directory: {dataset_path}")
    # Parse tasks if it's a string
    if isinstance(new_tasks, str):
        parsed_tasks = parse_task_input(new_tasks)
    else:
        parsed_tasks = new_tasks
    
    print(f"New task descriptions: {parsed_tasks}")
    if create_backup:
        print("Backup files will be created")
    else:
        print("No backup files will be created")
    print()
    
    # Update both files
    update_episodes_jsonl(episodes_file, parsed_tasks, create_backup)
    update_tasks_jsonl(tasks_file, parsed_tasks, create_backup)
    
    print()
    print("✅ Task descriptions updated successfully!")
    if create_backup:
        print("Backup files created with .backup extension")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Change task descriptions in a LeRobot dataset",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Single task
  python change_task_description.py ~/.cache/huggingface/lerobot/eliasab16/dataset "Pick up the red cube"
  
  # Multiple tasks as JSON list
  python change_task_description.py /path/to/dataset '["Pick up the cube", "Place the cube", "Push button"]' --backup
  
  # Multiple tasks as comma-separated
  python change_task_description.py /path/to/dataset "Pick up cube,Place cube,Push button" --backup
        """
    )
    
    parser.add_argument("dataset_dir", help="Path to the dataset directory")
    parser.add_argument("new_tasks", help="New task description(s) - can be a single task, JSON list like '[\"task1\", \"task2\"]', or comma-separated list like 'task1,task2'")
    parser.add_argument("--backup", action="store_true", default=False, 
                       help="Create backup files (default: False)")
    
    args = parser.parse_args()
    
    try:
        change_task_description(args.dataset_dir, args.new_tasks, args.backup)
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)