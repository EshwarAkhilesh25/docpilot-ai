"""Tests for database migration verification."""

from unittest.mock import MagicMock, patch

import pytest

from app.db.migration_verification import MigrationVerificationError, MigrationVerifier


class TestMigrationVerifier:
    """Tests for MigrationVerifier class."""

    def test_initialization(self):
        """Test that verifier initializes correctly."""
        verifier = MigrationVerifier()
        assert verifier._alembic_ini_path == "alembic.ini"
        assert verifier._versions_path.name == "versions"

    def test_initialization_custom_path(self):
        """Test verifier initialization with custom path."""
        verifier = MigrationVerifier("custom_alembic.ini")
        assert verifier._alembic_ini_path == "custom_alembic.ini"

    @patch("pathlib.Path.exists")
    @patch("pathlib.Path.glob")
    def test_get_head_revision_success(self, mock_glob, mock_exists):
        """Test successful head revision retrieval."""
        mock_exists.return_value = True
        mock_file = MagicMock()
        mock_file.name = "123_abc.py"
        mock_file.read_text.return_value = "revision = 'abc123'\\ndown_revision = None"
        mock_glob.return_value = [mock_file]

        verifier = MigrationVerifier()
        head = verifier._get_head_revision()

        assert head == "abc123"

    @patch("pathlib.Path.exists")
    def test_get_head_revision_no_migrations(self, mock_exists):
        """Test head revision when no migrations exist."""
        mock_exists.return_value = False

        verifier = MigrationVerifier()
        head = verifier._get_head_revision()

        assert head is None

    @patch("pathlib.Path.exists")
    def test_get_head_revision_error(self, mock_exists):
        """Test head revision retrieval error."""
        mock_exists.side_effect = Exception("File system error")

        verifier = MigrationVerifier()

        with pytest.raises(MigrationVerificationError, match="Failed to get head revision"):
            verifier._get_head_revision()

    @patch("sqlalchemy.create_engine")
    @patch("app.db.migration_verification.settings")
    def test_get_current_revision_success(self, mock_settings, mock_create_engine):
        """Test successful current revision retrieval."""
        mock_settings.DATABASE_URL = "postgresql+asyncpg://localhost/db"
        mock_engine = MagicMock()
        mock_connection = MagicMock()

        mock_result = MagicMock()
        mock_result.fetchone.return_value = ["abc123"]

        mock_connection.execute.return_value = mock_result
        mock_engine.connect.return_value.__enter__.return_value = mock_connection
        mock_create_engine.return_value = mock_engine

        verifier = MigrationVerifier()
        current = verifier.get_current_revision()

        assert current == "abc123"

    @patch("sqlalchemy.create_engine")
    @patch("app.db.migration_verification.settings")
    def test_get_current_revision_unreachable(self, mock_settings, mock_create_engine):
        """Test current revision when database is unreachable."""
        mock_settings.DATABASE_URL = "postgresql+asyncpg://localhost/db"
        mock_create_engine.side_effect = Exception("Connection refused")

        verifier = MigrationVerifier()
        current = verifier.get_current_revision()

        assert current is None

    @patch("app.db.migration_verification.MigrationVerifier.get_current_revision")
    @patch("app.db.migration_verification.MigrationVerifier._get_head_revision")
    def test_verify_migrations_up_to_date(self, mock_get_head, mock_get_current):
        """Test migration verification when up to date."""
        mock_get_head.return_value = "abc123"
        mock_get_current.return_value = "abc123"

        verifier = MigrationVerifier()
        status = verifier.verify_migrations()

        assert status["head_revision"] == "abc123"
        assert status["current_revision"] == "abc123"
        assert status["is_up_to_date"] is True
        assert status["has_pending_migrations"] is False
        assert status["error"] is None

    @patch("app.db.migration_verification.MigrationVerifier.get_current_revision")
    @patch("app.db.migration_verification.MigrationVerifier._get_head_revision")
    def test_verify_migrations_pending(self, mock_get_head, mock_get_current):
        """Test migration verification with pending migrations."""
        mock_get_head.return_value = "def456"
        mock_get_current.return_value = "abc123"

        verifier = MigrationVerifier()
        status = verifier.verify_migrations()

        assert status["head_revision"] == "def456"
        assert status["current_revision"] == "abc123"
        assert status["is_up_to_date"] is False
        assert status["has_pending_migrations"] is True
        assert status["error"] is None

    @patch("app.db.migration_verification.MigrationVerifier.get_current_revision")
    @patch("app.db.migration_verification.MigrationVerifier._get_head_revision")
    def test_verify_migrations_unreachable(self, mock_get_head, mock_get_current):
        """Test migration verification when database is unreachable."""
        mock_get_head.return_value = "abc123"
        mock_get_current.return_value = None

        verifier = MigrationVerifier()
        status = verifier.verify_migrations()

        assert status["head_revision"] == "abc123"
        assert status["current_revision"] is None
        assert status["is_up_to_date"] is False
        assert status["has_pending_migrations"] is True
        assert "unreachable" in status["error"].lower()

    @patch("app.db.migration_verification.MigrationVerifier.get_current_revision")
    @patch("app.db.migration_verification.MigrationVerifier._get_head_revision")
    def test_verify_migrations_no_migrations(self, mock_get_head, mock_get_current):
        """Test migration verification when no migrations exist."""
        mock_get_head.return_value = None

        verifier = MigrationVerifier()
        status = verifier.verify_migrations()

        assert status["head_revision"] is None
        assert status["current_revision"] is None
        assert status["is_up_to_date"] is False
        assert status["has_pending_migrations"] is True
        assert "no migrations found" in status["error"].lower()


class TestBootstrapMigrationVerification:
    """Tests for bootstrap database migration verification."""

    @patch("app.core.bootstrap.MigrationVerifier")
    @patch("app.core.bootstrap.settings")
    def test_verify_migrations_strict_mode_pending(self, mock_settings, mock_verifier_class):
        """Test strict mode fails with pending migrations."""
        from app.core.bootstrap import Bootstrap, MigrationVerificationError

        mock_settings.STRICT_MIGRATION_CHECK = True
        mock_verifier = MagicMock()
        mock_verifier.verify_migrations.return_value = {
            "head_revision": "def456",
            "current_revision": "abc123",
            "is_up_to_date": False,
            "has_pending_migrations": True,
            "error": None,
        }
        mock_verifier_class.return_value = mock_verifier

        bootstrap = Bootstrap()

        with pytest.raises(MigrationVerificationError, match="Pending migrations detected"):
            bootstrap.verify_database_migrations()

    @patch("app.core.bootstrap.MigrationVerifier")
    @patch("app.core.bootstrap.settings")
    def test_verify_migrations_non_strict_mode_pending(self, mock_settings, mock_verifier_class):
        """Test non-strict mode allows pending migrations with warning."""
        from app.core.bootstrap import Bootstrap

        mock_settings.STRICT_MIGRATION_CHECK = False
        mock_verifier = MagicMock()
        mock_verifier.verify_migrations.return_value = {
            "head_revision": "def456",
            "current_revision": "abc123",
            "is_up_to_date": False,
            "has_pending_migrations": True,
            "error": None,
        }
        mock_verifier_class.return_value = mock_verifier

        bootstrap = Bootstrap()

        # Should not raise
        bootstrap.verify_database_migrations()

    @patch("app.core.bootstrap.MigrationVerifier")
    @patch("app.core.bootstrap.settings")
    def test_verify_migrations_strict_mode_unreachable(self, mock_settings, mock_verifier_class):
        """Test strict mode fails when database is unreachable."""
        from app.core.bootstrap import Bootstrap, MigrationVerificationError

        mock_settings.STRICT_MIGRATION_CHECK = True
        mock_verifier = MagicMock()
        mock_verifier.verify_migrations.return_value = {
            "head_revision": "abc123",
            "current_revision": None,
            "is_up_to_date": False,
            "has_pending_migrations": True,
            "error": "Database unreachable",
        }
        mock_verifier_class.return_value = mock_verifier

        bootstrap = Bootstrap()

        with pytest.raises(MigrationVerificationError):
            bootstrap.verify_database_migrations()

    @patch("app.core.bootstrap.MigrationVerifier")
    @patch("app.core.bootstrap.settings")
    def test_verify_migrations_up_to_date(self, mock_settings, mock_verifier_class):
        """Test verification passes when up to date."""
        from app.core.bootstrap import Bootstrap

        mock_settings.STRICT_MIGRATION_CHECK = True
        mock_verifier = MagicMock()
        mock_verifier.verify_migrations.return_value = {
            "head_revision": "abc123",
            "current_revision": "abc123",
            "is_up_to_date": True,
            "has_pending_migrations": False,
            "error": None,
        }
        mock_verifier_class.return_value = mock_verifier

        bootstrap = Bootstrap()

        # Should not raise
        bootstrap.verify_database_migrations()

    @patch("app.core.bootstrap.MigrationVerifier")
    @patch("app.core.bootstrap.settings")
    def test_verify_migrations_not_initialized_strict(self, mock_settings, mock_verifier_class):
        """Test strict mode fails when database not initialized."""
        from app.core.bootstrap import Bootstrap, MigrationVerificationError

        mock_settings.STRICT_MIGRATION_CHECK = True
        mock_verifier = MagicMock()
        mock_verifier.verify_migrations.return_value = {
            "head_revision": None,
            "current_revision": None,
            "is_up_to_date": False,
            "has_pending_migrations": True,
            "error": "Database not initialized - no migrations found",
        }
        mock_verifier_class.return_value = mock_verifier

        bootstrap = Bootstrap()

        with pytest.raises(MigrationVerificationError):
            bootstrap.verify_database_migrations()

    @patch("app.core.bootstrap.MigrationVerifier")
    @patch("app.core.bootstrap.settings")
    def test_verify_migrations_not_initialized_non_strict(self, mock_settings, mock_verifier_class):
        """Test non-strict mode warns when database not initialized."""
        from app.core.bootstrap import Bootstrap

        mock_settings.STRICT_MIGRATION_CHECK = False
        mock_verifier = MagicMock()
        mock_verifier.verify_migrations.return_value = {
            "head_revision": None,
            "current_revision": None,
            "is_up_to_date": False,
            "has_pending_migrations": True,
            "error": "Database not initialized - no migrations found",
        }
        mock_verifier_class.return_value = mock_verifier

        bootstrap = Bootstrap()

        # Should not raise
        bootstrap.verify_database_migrations()
