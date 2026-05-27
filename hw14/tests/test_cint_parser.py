"""Тесты для CINT парсера."""

from pathlib import Path

from src.search.cint_parser import (
    extract_script_header,
    extract_used_apis,
    is_cint_script,
    parse_header_comment,
)


class TestCintParser:
    """Тесты CINT парсера."""

    def test_is_cint_script_by_location(self, tmp_path: Path):
        """Проверка определения CINT скрипта по расположению."""
        cint_file = tmp_path / "src" / "examples" / "l3" / "test.c"
        cint_file.parent.mkdir(parents=True)
        cint_file.write_text("int main() { return 0; }")

        assert is_cint_script(cint_file, tmp_path) is True

    def test_is_cint_script_by_header(self, tmp_path: Path):
        """Проверка определения CINT скрипта по заголовку."""
        cint_file = tmp_path / "test.c"
        cint_file.write_text("/*\n * Tested on: Tomahawk4\n * Tests: route\n */\nint main() {}")

        assert is_cint_script(cint_file, tmp_path) is True

    def test_not_cint_script(self, tmp_path: Path):
        """Обычный C файл не CINT скрипт."""
        c_file = tmp_path / "normal.c"
        c_file.write_text("int main() { return 0; }")

        assert is_cint_script(c_file, tmp_path) is False

    def test_extract_script_header(self, tmp_path: Path):
        """Извлечение заголовочного комментария."""
        cint_file = tmp_path / "test.c"
        cint_file.write_text(
            "/*\n * L3 Route Basic Example\n * Tested on: Tomahawk4 (BCM56980)\n */\nint main() {}"
        )

        header = extract_script_header(cint_file)
        assert header is not None
        assert "Tomahawk4" in header
        assert "L3 Route Basic Example" in header

    def test_extract_script_header_no_comment(self, tmp_path: Path):
        """Файл без комментария."""
        c_file = tmp_path / "test.c"
        c_file.write_text("int main() { return 0; }")

        header = extract_script_header(c_file)
        assert header is None

    def test_parse_header_comment(self):
        """Парсинг заголовочного комментария."""
        comment = (
            "/*\n"
            " * L3 Route Basic Example\n"
            " * Tested on: Tomahawk4 (BCM56980)\n"
            " * Ports: 0-31\n"
            " * Tests: basic_route / vlan_create / mpls\n"
            " */"
        )

        result = parse_header_comment(comment)
        assert result["chip"] == "Tomahawk4"
        assert result["ports"] == "0-31"
        assert "basic_route" in result["tests"]
        assert "mpls" in result["tests"]

    def test_extract_used_apis(self, tmp_path: Path):
        """Извлечение используемых API."""
        cint_file = tmp_path / "test.c"
        cint_file.write_text(
            "#include <bcm/l3.h>\n"
            "int test() {\n"
            "    bcm_l3_route_add(unit, &route);\n"
            "    bcm_l3_route_get(unit, &route);\n"
            "    return 0;\n"
            "}"
        )

        apis = extract_used_apis(cint_file)
        assert "bcm_l3_route_add" in apis
        assert "bcm_l3_route_get" in apis
