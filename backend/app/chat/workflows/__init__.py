"""Workflow plugins initialization and registration."""

from app.chat.workflows.action_items import ActionItemsWorkflow
from app.chat.workflows.compare import CompareWorkflow
from app.chat.workflows.explain import ExplainWorkflow
from app.chat.workflows.key_findings import KeyFindingsWorkflow
from app.chat.workflows.mcq import MCQWorkflow
from app.chat.workflows.qa import GeneralQAWorkflow
from app.chat.workflows.registry import registry
from app.chat.workflows.summarize import SummarizeWorkflow
from app.chat.workflows.timeline import TimelineWorkflow


def register_workflows():
    """Register all available workflow plugins."""
    registry.register(GeneralQAWorkflow)
    registry.register(SummarizeWorkflow)
    registry.register(MCQWorkflow)
    registry.register(CompareWorkflow)
    registry.register(KeyFindingsWorkflow)
    registry.register(ExplainWorkflow)
    registry.register(TimelineWorkflow)
    registry.register(ActionItemsWorkflow)


register_workflows()
