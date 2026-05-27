"""Sandbox — защита от path traversal при доступе к файлам SDK."""

from pathlib import Path


class SecurityError(Exception):
    """Ошибка безопасности при попытке доступа вне sandbox."""

    pass


class PathGuard:
    """Защита от path traversal.

    Все пути проверяются на принадлежность SDK_ROOT.
    Запрещены: path traversal (..), симлинки наружу, абсолютные пути вне SDK_ROOT.
    """

    def __init__(self, sdk_root: Path) -> None:
        """Инициализация PathGuard.

        Args:
            sdk_root: Корневая директория SDK (разрешённая зона).
        """
        self.sdk_root = sdk_root.resolve()

    def validate(self, path: str) -> Path:
        """Проверить, что path находится внутри sdk_root.

        Аргумент path интерпретируется как относительный от sdk_root.

        Args:
            path: Путь для проверки (относительный или абсолютный).

        Returns:
            Resolved path внутри sdk_root.

        Raises:
            SecurityError: Если path указывает за пределы sdk_root или является симлинком.
            FileNotFoundError: Если path не существует.
        """
        resolved = (self.sdk_root / path).resolve()

        if not str(resolved).startswith(str(self.sdk_root)):
            raise SecurityError(f"Path traversal detected: {path} -> {resolved}")

        if resolved.is_symlink():
            raise SecurityError(f"Symlinks are not allowed: {resolved}")

        if not resolved.exists():
            raise FileNotFoundError(f"Path does not exist: {resolved}")

        return resolved

    def validate_absolute(self, path: str) -> Path:
        """Проверить абсолютный путь.

        Путь уже должен быть внутри sdk_root (не конкатенируется).

        Args:
            path: Абсолютный путь для проверки.

        Returns:
            Resolved path.

        Raises:
            SecurityError: Если путь вне sdk_root.
        """
        resolved = Path(path).resolve()

        if not str(resolved).startswith(str(self.sdk_root)):
            raise SecurityError(f"Path outside sandbox: {resolved}")

        return resolved
