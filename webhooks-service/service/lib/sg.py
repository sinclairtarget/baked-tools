def update_linked_tasks(project_id, shot_id, task_statuses):
    """
    For the given shot, finds all linked tasks and updates their status.

    If a linked task already has a status in the list task_statuses, the linked
    task is not updated. Otherwise, the linked task has its status updated
    to the first status in task_statuses.

    Returns a list of tasks that were updated.
    """
    return []
