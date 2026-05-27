"""Тесты для парсера макросов."""

from src.search.macro_parser import extract_chip_conditions, extract_chip_guards, extract_macros


class TestMacroParser:
    """Тесты MacroParser."""

    def test_extract_macros(self):
        """Извлечение #define макросов."""
        lines = [
            "#define BCM56980_DEVICE_ID 0x56980",
            "#define BCM_TOMAHAWK4_SUPPORT",
            "int bcm_vlan_create(int unit);",
        ]
        macros = extract_macros(lines)
        assert len(macros) == 2
        assert macros[0].name == "BCM56980_DEVICE_ID"
        assert macros[0].value == "0x56980"
        assert macros[1].name == "BCM_TOMAHAWK4_SUPPORT"

    def test_extract_chip_guards(self):
        """Извлечение chip guard условий."""
        lines = [
            "#include <bcm/l2.h>",
            "#if defined(BCM_TOMAHAWK4_SUPPORT)",
            "int th4_l2_entry_insert(int unit);",
            "#endif",
        ]
        guards = extract_chip_guards(lines, func_line=2)
        assert "BCM_TOMAHAWK4_SUPPORT" in guards

    def test_extract_chip_conditions(self):
        """Извлечение SOC_IS_* условий."""
        lines = [
            "int bcm_esw_l2_addr_add(int unit) {",
            "    if (SOC_IS_TOMAHAWK4(unit)) {",
            "        return th4_l2_entry_insert(unit);",
            "    }",
            "    return BCM_E_UNAVAIL;",
            "}",
        ]
        conditions = extract_chip_conditions(lines, func_line=0)
        assert "SOC_IS_TOMAHAWK4(unit)" in conditions
