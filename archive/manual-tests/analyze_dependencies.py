import inspect
import sys
from pathlib import Path

# Add the app directory to the path
sys.path.insert(0, str(Path(__file__).parent))

# Import all the dependency functions
from app.api.dependencies import (
    get_uow,
    get_user_service,
    get_authentication_service,
    get_llm_provider,
    get_embedding_provider,
    get_transcription_provider,
    get_storage_provider,
    get_vector_index_provider,
    get_keyword_index_provider,
    get_retriever_service,
    get_current_user,
    get_db,
)

from app.api.v1.documents import (
    get_document_service,
    get_processing_status_service,
    get_document_download_service,
)

from app.api.v1.chat import (
    get_chat_service,
    get_conversation_service,
)

from app.dependencies.common import get_database

# List of all dependency functions to analyze
dependency_functions = [
    # From app.api.dependencies
    get_uow,
    get_user_service,
    get_authentication_service,
    get_llm_provider,
    get_embedding_provider,
    get_transcription_provider,
    get_storage_provider,
    get_vector_index_provider,
    get_keyword_index_provider,
    get_retriever_service,
    get_current_user,
    get_db,
    # From app.api.v1.documents
    get_document_service,
    get_processing_status_service,
    get_document_download_service,
    # From app.api.v1.chat
    get_chat_service,
    get_conversation_service,
    # From app.dependencies.common
    get_database,
]

print("=" * 80)
print("DEPENDENCY FUNCTION SIGNATURE ANALYSIS")
print("=" * 80)

for func in dependency_functions:
    print(f"\nFunction: {func.__name__}")
    print(f"Module: {func.__module__}")
    print(f"File: {inspect.getfile(func)}")
    print(f"Line: {inspect.getsourcelines(func)[1]}")
    print(f"Type: {type(func)}")
    print(f"Callable: {callable(func)}")

    try:
        sig = inspect.signature(func)
        print(f"Signature: {sig}")

        # Check for *args and **kwargs
        has_args = any(
            param.kind == inspect.Parameter.VAR_POSITIONAL
            for param in sig.parameters.values()
        )
        has_kwargs = any(
            param.kind == inspect.Parameter.VAR_KEYWORD
            for param in sig.parameters.values()
        )

        print(f"Has *args: {has_args}")
        print(f"Has **kwargs: {has_kwargs}")

        # Print parameter details
        print("Parameters:")
        for param_name, param in sig.parameters.items():
            print(
                f"  {param_name}: {param.annotation if param.annotation != inspect.Parameter.empty else 'no annotation'}"
            )
            print(f"    kind: {param.kind.name}")
            print(
                f"    default: {param.default if param.default != inspect.Parameter.empty else 'no default'}"
            )

    except Exception as e:
        print(f"Error getting signature: {e}")

    print("-" * 80)

print("\n" + "=" * 80)
print("ANALYSIS COMPLETE")
print("=" * 80)
