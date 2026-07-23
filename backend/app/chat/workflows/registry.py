"""Registry for Workflow Plugins."""

from app.chat.workflows.base import WorkflowStrategy


class WorkflowRegistry:
    """Central registry for all AI workflows."""

    def __init__(self):
        self._workflows: dict[str, WorkflowStrategy] = {}

    def register(self, workflow_cls: type[WorkflowStrategy]) -> None:
        """Register a workflow class. Instances are created lazily or we just register instances."""
        workflow = workflow_cls()
        self._workflows[workflow.intent_name] = workflow

    def get_workflow(self, intent_name: str) -> WorkflowStrategy:
        """Get a workflow by intent name. Defaults to GENERAL_QA if not found."""
        if intent_name in self._workflows:
            return self._workflows[intent_name]

        # Fallback
        return self._workflows["GENERAL_QA"]  # type: ignore


# Global registry instance
registry = WorkflowRegistry()
