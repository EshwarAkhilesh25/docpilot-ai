"""Tests for application bootstrap."""

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from app.core.bootstrap import (
    Bootstrap,
    ProviderRegistry,
    get_bootstrap,
    initialize_application,
    shutdown_application,
)


class TestProviderRegistry:
    """Tests for ProviderRegistry class."""

    def test_registry_initialization(self):
        """Test that registry initializes correctly."""
        registry = ProviderRegistry()
        assert registry._factories == {}
        assert registry._instances == {}

    def test_register_factory(self):
        """Test registering a provider factory."""
        registry = ProviderRegistry()

        def factory():
            return MagicMock()

        registry.register("test_provider", factory)

        assert "test_provider" in registry._factories
        assert registry._factories["test_provider"] is factory

    def test_get_provider_creates_instance(self):
        """Test that getting a provider creates an instance."""
        registry = ProviderRegistry()
        mock_instance = MagicMock()

        def factory():
            return mock_instance

        registry.register("test_provider", factory)

        instance = registry.get("test_provider")

        assert instance is mock_instance
        assert "test_provider" in registry._instances

    def test_get_provider_reuses_instance(self):
        """Test that getting a provider reuses existing instance."""
        registry = ProviderRegistry()
        mock_instance = MagicMock()

        def factory():
            return mock_instance

        registry.register("test_provider", factory)

        instance1 = registry.get("test_provider")
        instance2 = registry.get("test_provider")

        assert instance1 is instance2

    def test_has_provider(self):
        """Test checking if provider is registered."""
        registry = ProviderRegistry()

        def factory():
            return MagicMock()

        registry.register("test_provider", factory)

        assert registry.has("test_provider") is True
        assert registry.has("nonexistent") is False

    def test_get_nonexistent_provider_raises(self):
        """Test that getting nonexistent provider raises KeyError."""
        registry = ProviderRegistry()

        with pytest.raises(KeyError, match="Provider factory not registered"):
            registry.get("nonexistent")

    def test_clear_instances(self):
        """Test clearing provider instances."""
        registry = ProviderRegistry()

        def factory():
            return MagicMock()

        registry.register("test_provider", factory)

        registry.get("test_provider")
        assert "test_provider" in registry._instances

        registry.clear()
        assert registry._instances == {}
        assert "test_provider" in registry._factories  # Factories should remain


class TestBootstrap:
    """Tests for Bootstrap class."""

    def test_bootstrap_initialization(self):
        """Test that bootstrap initializes correctly."""
        bootstrap = Bootstrap()
        assert bootstrap._initialized is False
        assert isinstance(bootstrap._provider_registry, ProviderRegistry)

    def test_validate_configuration_valid(self):
        """Test configuration validation with valid settings."""
        bootstrap = Bootstrap()
        # Should not raise any exception
        bootstrap.validate_configuration()

    def test_validate_configuration_production_invalid_secret(self):
        """Test that production mode requires changing JWT_SECRET."""
        bootstrap = Bootstrap()
        with patch("app.core.bootstrap.settings") as mock_settings:
            mock_settings.APP_ENV = "production"
            mock_settings.JWT_SECRET = "change-this-secret-in-production"
            mock_settings.GROQ_API_KEY = "valid-key"
            mock_settings.STORAGE_PATH = "/storage"
            mock_settings.FAISS_INDEX_PATH = "/faiss"

            with pytest.raises(ValueError, match="JWT_SECRET must be changed"):
                bootstrap.validate_configuration()

    def test_validate_configuration_production_valid_secret(self):
        """Test that production mode accepts changed JWT_SECRET."""
        bootstrap = Bootstrap()
        with patch("app.core.bootstrap.settings") as mock_settings:
            mock_settings.APP_ENV = "production"
            mock_settings.JWT_SECRET = "changed-secret"
            mock_settings.GROQ_API_KEY = "valid-key"
            mock_settings.STORAGE_PATH = "/storage"
            mock_settings.FAISS_INDEX_PATH = "/faiss"

            # Should not raise
            bootstrap.validate_configuration()

    def test_validate_configuration_relative_paths_warning(self):
        """Test that relative paths trigger warnings but don't fail."""
        bootstrap = Bootstrap()
        with patch("app.core.bootstrap.settings") as mock_settings:
            mock_settings.APP_ENV = "development"
            mock_settings.JWT_SECRET = "any-secret"
            mock_settings.GROQ_API_KEY = ""
            mock_settings.STORAGE_PATH = "storage/uploads"  # relative
            mock_settings.FAISS_INDEX_PATH = "storage/faiss"  # relative

            # Should not raise, just log warnings
            bootstrap.validate_configuration()

    def test_verify_storage_directories(self, tmp_path):
        """Test that storage directories are created."""
        bootstrap = Bootstrap()
        with patch("app.core.bootstrap.settings") as mock_settings:
            mock_settings.STORAGE_PATH = str(tmp_path / "storage")
            mock_settings.FAISS_INDEX_PATH = str(tmp_path / "faiss")

            bootstrap.verify_storage_directories()

            assert Path(mock_settings.STORAGE_PATH).exists()
            assert Path(mock_settings.FAISS_INDEX_PATH).exists()

    def test_verify_storage_directories_existing(self, tmp_path):
        """Test that existing directories are not recreated."""
        storage_path = tmp_path / "storage"
        faiss_path = tmp_path / "faiss"
        storage_path.mkdir(parents=True)
        faiss_path.mkdir(parents=True)

        bootstrap = Bootstrap()
        with patch("app.core.bootstrap.settings") as mock_settings:
            mock_settings.STORAGE_PATH = str(storage_path)
            mock_settings.FAISS_INDEX_PATH = str(faiss_path)

            # Should not raise even if directories exist
            bootstrap.verify_storage_directories()

    def test_register_provider_factories_with_api_key(self):
        """Test provider factory registration when API key is configured."""
        bootstrap = Bootstrap()
        with patch("app.core.bootstrap.settings") as mock_settings:
            mock_settings.GROQ_API_KEY = "valid-api-key"
            mock_settings.STORAGE_PATH = "storage/uploads"
            mock_settings.FAISS_INDEX_PATH = "storage/faiss"
            mock_settings.EMBEDDING_MODEL = "BAAI/bge-small-en-v1.5"
            mock_settings.WHISPER_MODEL = "whisper-large-v3"

            bootstrap.register_provider_factories()

            assert bootstrap._provider_registry.has("storage")
            assert bootstrap._provider_registry.has("embedding")
            assert bootstrap._provider_registry.has("vector_index")
            assert bootstrap._provider_registry.has("llm")
            assert bootstrap._provider_registry.has("transcription")

    def test_register_provider_factories_without_api_key(self):
        """Test provider factory registration when API key is not configured."""
        bootstrap = Bootstrap()
        with patch("app.core.bootstrap.settings") as mock_settings:
            mock_settings.GROQ_API_KEY = ""
            mock_settings.STORAGE_PATH = "storage/uploads"
            mock_settings.FAISS_INDEX_PATH = "storage/faiss"
            mock_settings.EMBEDDING_MODEL = "BAAI/bge-small-en-v1.5"
            mock_settings.WHISPER_MODEL = "whisper-large-v3"

            bootstrap.register_provider_factories()

            assert bootstrap._provider_registry.has("storage")
            assert bootstrap._provider_registry.has("embedding")
            assert bootstrap._provider_registry.has("vector_index")
            # LLM and transcription providers should not be registered without API key
            assert not bootstrap._provider_registry.has("llm")
            assert not bootstrap._provider_registry.has("transcription")

    @pytest.mark.asyncio
    async def test_shutdown_with_providers(self):
        """Test graceful shutdown with all providers."""
        bootstrap = Bootstrap()

        # Mock providers with close methods
        mock_llm = MagicMock()
        mock_llm.close = MagicMock(return_value=None)
        mock_transcription = MagicMock()
        mock_transcription.close = MagicMock(return_value=None)

        # Register providers directly in registry
        bootstrap._provider_registry.register("llm", lambda: mock_llm)
        bootstrap._provider_registry.register("transcription", lambda: mock_transcription)

        # Instantiate them
        bootstrap._provider_registry.get("llm")
        bootstrap._provider_registry.get("transcription")

        await bootstrap.shutdown()

        mock_llm.close.assert_called_once()
        mock_transcription.close.assert_called_once()

    @pytest.mark.asyncio
    async def test_shutdown_without_providers(self):
        """Test graceful shutdown without providers."""
        bootstrap = Bootstrap()

        # Should not raise even without providers
        await bootstrap.shutdown()

    def test_log_startup_info(self):
        """Test startup information logging."""
        bootstrap = Bootstrap()
        bootstrap._provider_registry.register("storage", lambda: MagicMock())
        bootstrap._provider_registry.register("embedding", lambda: MagicMock())
        bootstrap._provider_registry.register("transcription", lambda: MagicMock())
        bootstrap._provider_registry.register("llm", lambda: MagicMock())
        bootstrap._provider_registry.register("vector_index", lambda: MagicMock())

        with patch("app.core.bootstrap.settings") as mock_settings:
            mock_settings.APP_NAME = "DocMind API"
            mock_settings.APP_VERSION = "0.1.0"
            mock_settings.APP_ENV = "development"
            mock_settings.DEBUG = True
            mock_settings.STORAGE_PATH = "storage/uploads"
            mock_settings.FAISS_INDEX_PATH = "storage/faiss"
            mock_settings.EMBEDDING_MODEL = "BAAI/bge-small-en-v1.5"

            # Should not raise
            bootstrap.log_startup_info()

    def test_get_provider_methods(self):
        """Test provider getter methods."""
        bootstrap = Bootstrap()

        mock_llm = MagicMock()
        mock_embedding = MagicMock()
        mock_transcription = MagicMock()
        mock_storage = MagicMock()
        mock_vector = MagicMock()

        bootstrap._provider_registry.register("llm", lambda: mock_llm)
        bootstrap._provider_registry.register("embedding", lambda: mock_embedding)
        bootstrap._provider_registry.register("transcription", lambda: mock_transcription)
        bootstrap._provider_registry.register("storage", lambda: mock_storage)
        bootstrap._provider_registry.register("vector_index", lambda: mock_vector)

        assert bootstrap.get_llm_provider() is mock_llm
        assert bootstrap.get_embedding_provider() is mock_embedding
        assert bootstrap.get_transcription_provider() is mock_transcription
        assert bootstrap.get_storage_provider() is mock_storage
        assert bootstrap.get_vector_index_provider() is mock_vector

    def test_get_provider_returns_none_if_not_registered(self):
        """Test that getter methods return None if provider not registered."""
        bootstrap = Bootstrap()

        assert bootstrap.get_llm_provider() is None
        assert bootstrap.get_embedding_provider() is None
        assert bootstrap.get_transcription_provider() is None
        assert bootstrap.get_storage_provider() is None
        assert bootstrap.get_vector_index_provider() is None


class TestGlobalBootstrap:
    """Tests for global bootstrap instance."""

    def test_get_bootstrap_singleton(self):
        """Test that get_bootstrap returns the same instance."""
        bootstrap1 = get_bootstrap()
        bootstrap2 = get_bootstrap()
        assert bootstrap1 is bootstrap2

    @pytest.mark.asyncio
    async def test_initialize_application(self, tmp_path):
        """Test full application initialization."""
        with patch("app.core.bootstrap.settings") as mock_settings:
            mock_settings.APP_ENV = "development"
            mock_settings.JWT_SECRET = "test-secret"
            mock_settings.GROQ_API_KEY = ""
            mock_settings.STORAGE_PATH = str(tmp_path / "storage")
            mock_settings.FAISS_INDEX_PATH = str(tmp_path / "faiss")
            mock_settings.EMBEDDING_MODEL = "BAAI/bge-small-en-v1.5"
            mock_settings.WHISPER_MODEL = "whisper-large-v3"
            mock_settings.APP_NAME = "DocMind API"
            mock_settings.APP_VERSION = "0.1.0"
            mock_settings.DEBUG = True
            mock_settings.STRICT_MIGRATION_CHECK = False

            # Mock migration verification
            with patch("app.core.bootstrap.MigrationVerifier") as mock_verifier_class:
                mock_verifier = MagicMock()
                mock_verifier.verify_migrations.return_value = {
                    "head_revision": "abc123",
                    "current_revision": "abc123",
                    "is_up_to_date": True,
                    "has_pending_migrations": False,
                    "error": None,
                }
                mock_verifier_class.return_value = mock_verifier

                bootstrap = await initialize_application()

                assert bootstrap is not None
                assert isinstance(bootstrap._provider_registry, ProviderRegistry)

    @pytest.mark.asyncio
    async def test_initialize_application_invalid_config(self):
        """Test that initialization fails with invalid configuration."""
        with patch("app.core.bootstrap.settings") as mock_settings:
            mock_settings.APP_ENV = "production"
            mock_settings.JWT_SECRET = "change-this-secret-in-production"
            mock_settings.GROQ_API_KEY = ""
            mock_settings.STORAGE_PATH = "/storage"
            mock_settings.FAISS_INDEX_PATH = "/faiss"
            mock_settings.STRICT_MIGRATION_CHECK = False

            with pytest.raises(ValueError):
                await initialize_application()

    @pytest.mark.asyncio
    async def test_shutdown_application(self):
        """Test global shutdown function."""
        bootstrap = get_bootstrap()
        mock_llm = MagicMock()
        mock_llm.close = MagicMock(return_value=None)
        bootstrap._provider_registry.register("llm", lambda: mock_llm)
        bootstrap._provider_registry.get("llm")

        await shutdown_application()

        mock_llm.close.assert_called_once()
