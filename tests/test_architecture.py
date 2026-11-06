import ast
import importlib
from pathlib import Path
import unittest


PACKAGE_ROOT = Path(__file__).resolve().parents[1] / "src" / "request_system"
LAYER_PREFIXES = {
    "presentation": {"repositories", "infrastructure"},
    "services": {"presentation", "infrastructure"},
    "repositories": {"presentation", "services", "infrastructure"},
    "infrastructure": {"presentation", "services"},
}


def imported_request_system_modules(source: Path):
    tree = ast.parse(source.read_text(encoding="utf-8"), filename=str(source))
    relative_parts = list(source.relative_to(PACKAGE_ROOT).with_suffix("").parts)
    if relative_parts[-1] == "__init__":
        relative_parts.pop()
    else:
        relative_parts.pop()

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                if alias.name == "request_system" or alias.name.startswith("request_system."):
                    yield alias.name
        elif isinstance(node, ast.ImportFrom):
            if node.module == "request_system" or (node.module or "").startswith("request_system."):
                yield node.module
            elif node.level:
                base = relative_parts[: len(relative_parts) - node.level + 1]
                suffix = (node.module or "").split(".") if node.module else []
                resolved = ".".join(["request_system", *base, *suffix])
                yield resolved


class ArchitectureLayerTests(unittest.TestCase):
    def test_layer_packages_are_importable(self) -> None:
        packages = (
            "request_system.presentation",
            "request_system.services",
            "request_system.repositories",
            "request_system.infrastructure.database",
        )

        for package in packages:
            with self.subTest(package=package):
                self.assertIsNotNone(importlib.import_module(package))

    def test_source_imports_respect_layer_boundaries(self) -> None:
        violations = []
        for source in PACKAGE_ROOT.rglob("*.py"):
            parts = source.relative_to(PACKAGE_ROOT).parts
            source_layer = parts[0] if parts and parts[0] in LAYER_PREFIXES else None
            if source_layer is None:
                continue

            for imported in imported_request_system_modules(source):
                parts = imported.split(".")
                if len(parts) < 2:
                    continue
                target_layer = parts[1]
                if target_layer in LAYER_PREFIXES[source_layer]:
                    violations.append(
                        f"{source.relative_to(PACKAGE_ROOT)} imports {imported}"
                    )

        self.assertEqual(violations, [], "Layer dependency violations:\n" + "\n".join(violations))


if __name__ == "__main__":
    unittest.main()
