"""Utilities used in generating docs."""

import ast
import importlib
import inspect
import typing
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent


def linkcode_resolve(source_url: str, domain: str, info: dict[str, str]) -> typing.Optional[str]:
    """
    Function called by linkcode to get the URL for a given resource.

    See for more details:
    https://www.sphinx-doc.org/en/master/usage/extensions/linkcode.html#confval-linkcode_resolve
    """
    if domain != "py":
        raise Exception("Unknown domain passed to linkcode function.")

    symbol_name = info["fullname"]

    module = importlib.import_module(info["module"])

    symbol = [module]
    for name in symbol_name.split("."):
        symbol.append(getattr(symbol[-1], name))
        symbol_name = name

    try:
        lines, start = inspect.getsourcelines(symbol[-1])
        end = start + len(lines)
    except TypeError:
        # Find variables by parsing the ast
        source = ast.parse(inspect.getsource(symbol[-2]))
        while isinstance(source.body[0], ast.ClassDef):
            source = source.body[0]

        for ast_obj in source.body:
            if isinstance(ast_obj, ast.Assign):
                names = []
                for target in ast_obj.targets:
                    if isinstance(target, ast.Tuple):
                        names.extend([name.id for name in target.elts])
                    else:
                        names.append(target.id)

                if symbol_name in names:
                    start, end = ast_obj.lineno, ast_obj.end_lineno
                    break
        else:
            raise Exception(f"Could not find symbol `{symbol_name}` in {module.__name__}.")

        _, offset = inspect.getsourcelines(symbol[-2])
        if offset != 0:
            offset -= 1
        start += offset
        end += offset

    file = Path(inspect.getfile(module)).relative_to(PROJECT_ROOT).as_posix()

    url = f"{source_url}/{file}#L{start}"
    if end != start:
        url += f"-L{end}"

    return url


def cleanup() -> None:
    """Remove unneeded autogenerated doc files, and clean up others."""
    included = __get_included()

    for file in (PROJECT_ROOT / "docs" / "output").iterdir():
        if file.name in ("botcore.rst", "botcore.exts.rst", "botcore.utils.rst") and file.name in included:
            content = file.read_text(encoding="utf-8").splitlines(keepends=True)

            # Rename the extension to be less wordy
            # Example: botcore.exts -> Botcore Exts
            title = content[0].split()[0].strip().replace("botcore.", "").replace(".", " ").title()
            title = f"{title}\n{'=' * len(title)}\n\n"
            content[0:2] = title

            file.write_text("".join(content), encoding="utf-8")

        elif file.name in included:
            # Clean up the submodule name so it's just the name without the top level module name
            # example: `botcore.regex module` -> `regex`
            lines = file.read_text(encoding="utf-8").splitlines(keepends=True)
            lines[0] = lines[0].replace("module", "").strip().split(".")[-1] + "\n"
            file.write_text("".join(lines))

        else:
            # These are files that have not been explicitly included in the docs via __all__
            print("Deleted file", file.name)
            file.unlink()
            continue

        # Take the opportunity to configure autodoc
        content = file.read_text(encoding="utf-8").replace("undoc-members", "special-members")
        file.write_text(content, encoding="utf-8")


def __get_included() -> set[str]:
    """Get a list of files that should be included in the final build."""

    def get_all_from_module(module_name: str) -> set[str]:
        module = importlib.import_module(module_name)
        _modules = {module.__name__ + ".rst"}

        if hasattr(module, "__all__"):
            for sub_module in module.__all__:
                _modules.update(get_all_from_module(sub_module))

        return _modules

    return get_all_from_module("botcore")
