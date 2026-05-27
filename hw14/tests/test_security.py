"""Тесты PathGuard с фейковым SDK."""

from pathlib import Path

import pytest

from src.security.path_guard import PathGuard, SecurityError


@pytest.fixture
def fake_sdk_root(tmp_path: Path) -> Path:
    """Создать временную структуру фейкового SDK."""
    sdk_root = tmp_path / "sdk"
    (sdk_root / "include/bcm").mkdir(parents=True)
    (sdk_root / "src").mkdir()
    (sdk_root / "include/bcm/vlan.h").write_text("int bcm_vlan_create(int unit);")
    return sdk_root


class TestPathGuard:
    """Тесты PathGuard."""

    def test_valid_path(self, fake_sdk_root: Path):
        """Успешная валидация пути внутри SDK."""
        guard = PathGuard(fake_sdk_root)
        result = guard.validate("include/bcm/vlan.h")
        assert result == (fake_sdk_root / "include/bcm/vlan.h").resolve()
        assert result.exists()

    def test_path_traversal_simple(self, fake_sdk_root: Path):
        """Path traversal (..) — ожидается SecurityError."""
        guard = PathGuard(fake_sdk_root)
        with pytest.raises(SecurityError, match="Path traversal"):
            guard.validate("../../etc/passwd")

    def test_path_traversal_double(self, fake_sdk_root: Path):
        """Path traversal с двойным .. — ожидается SecurityError."""
        guard = PathGuard(fake_sdk_root)
        with pytest.raises(SecurityError):
            guard.validate("include/../../../etc/passwd")

    def test_absolute_path_outside(self, fake_sdk_root: Path):
        """Абсолютный путь вне SDK — ожидается SecurityError."""
        guard = PathGuard(fake_sdk_root)
        with pytest.raises(SecurityError, match="Path traversal"):
            guard.validate("/etc/passwd")

    def test_nonexistent_path(self, fake_sdk_root: Path):
        """Несуществующий путь — ожидается FileNotFoundError."""
        guard = PathGuard(fake_sdk_root)
        with pytest.raises(FileNotFoundError):
            guard.validate("include/bcm/nonexistent.h")

    def test_root_path(self, fake_sdk_root: Path):
        """Путь к корню SDK."""
        guard = PathGuard(fake_sdk_root)
        result = guard.validate(".")
        assert result == fake_sdk_root.resolve()
        assert result.exists()

    def test_validate_absolute_inside(self, fake_sdk_root: Path):
        """Валидация абсолютного пути внутри SDK."""
        guard = PathGuard(fake_sdk_root)
        target = fake_sdk_root / "include/bcm/vlan.h"
        result = guard.validate_absolute(str(target))
        assert result == target.resolve()

    def test_validate_absolute_outside(self, fake_sdk_root: Path):
        """Валидация абсолютного пути вне SDK."""
        guard = PathGuard(fake_sdk_root)
        with pytest.raises(SecurityError, match="outside sandbox"):
            guard.validate_absolute("/tmp")
