from os import urandom
from subprocess import run
from tempfile import NamedTemporaryFile
import unittest

enc = "tests/k384.enc.py"
dec = "tests/k384.dec.py"


class Test(unittest.TestCase):
    def test_cmd(self):
        with (
            NamedTemporaryFile(delete_on_close=False) as src1,
            NamedTemporaryFile(delete_on_close=False) as out1,
            NamedTemporaryFile(delete_on_close=False) as out2,
        ):
            src1.write(urandom(1 * 1024 * 1024))
            src1.close()
            with open(src1.name, "rb") as inp:
                cp = run(["python3", enc], stdin=inp, stdout=out1)
            with open(out1.name, "rb") as inp:
                cp = run(["python3", dec], stdin=inp, stdout=out2)
            md1 = run(["md5sum", src1.name], capture_output=True).stdout
            md2 = run(["md5sum", out2.name], capture_output=True).stdout
            print(md1)
            print(md2)
            self.assertEqual(md1.split()[0], md2.split()[0])

    def test_cmd_b(self):
        with (
            NamedTemporaryFile(delete_on_close=False) as src1,
            NamedTemporaryFile(delete_on_close=False) as out1,
            NamedTemporaryFile(delete_on_close=False) as out2,
        ):
            src1.write(urandom(1 * 1024 * 1024))
            src1.close()
            with open(src1.name, "rb") as inp:
                cp = run(["python3", enc, "-b"], stdin=inp, stdout=out1)
            with open(out1.name, "rb") as inp:
                cp = run(["python3", dec, "-b"], stdin=inp, stdout=out2)
            md1 = run(["md5sum", src1.name], capture_output=True).stdout
            md2 = run(["md5sum", out2.name], capture_output=True).stdout
            print(md1)
            print(md2)
            self.assertEqual(md1.split()[0], md2.split()[0])

    def test_cmd_mod(self):
        menc = import_module_from_path(enc)
        mdec = import_module_from_path(dec)
        with (
            NamedTemporaryFile(delete_on_close=False) as src1,
            NamedTemporaryFile(delete_on_close=False) as out1,
            NamedTemporaryFile(delete_on_close=False) as out2,
        ):
            src1.write(urandom(1 * 1024 * 1024))
            src1.close()
            with open(src1.name, "rb") as inp:
                menc.enc(inp, out1)
                out1.close()
            # run(["stat", out1.name])
            with open(out1.name, "rb") as inp:
                mdec.dec(inp, out2)
                out2.close()
            md1 = run(["md5sum", src1.name], capture_output=True).stdout
            md2 = run(["md5sum", out2.name], capture_output=True).stdout
            print(md1)
            print(md2)
            # run(["stat", out2.name])
            # run(["cat", out2.name])
            self.assertEqual(md1.split()[0], md2.split()[0])


import importlib.util
import sys
from pathlib import Path  # Better path handling
from typing import Any


def import_module_from_path(module_path: str, module_name: str = None) -> Any:
    """
    Import a Python module from a file path.

    Args:
        module_path (str): Path to the .py file.
        module_name (str, optional): Name to assign to the module.
                                   If None, uses the file's stem.

    Returns:
        The imported module.

    Raises:
        FileNotFoundError: If the module_path does not exist.
        ImportError: If the module cannot be loaded.
    """
    module_path = Path(module_path).absolute()  # Convert to absolute path

    if not module_path.exists():
        raise FileNotFoundError(f"Module not found at: {module_path}")

    if module_name is None:
        module_name = module_path.stem  # Use filename without .py

    # Load the module
    spec = importlib.util.spec_from_file_location(module_name, str(module_path))
    if spec is None:
        raise ImportError(f"Could not load spec for module: {module_name}")

    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module  # Register in sys.modules

    try:
        spec.loader.exec_module(module)  # Execute the module
    except Exception as e:
        del sys.modules[module_name]  # Cleanup if loading fails
        raise ImportError(f"Failed to import {module_name}: {str(e)}")

    return module


if __name__ == "__main__":
    unittest.main()
