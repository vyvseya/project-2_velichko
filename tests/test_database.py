import json
import os
from contextlib import redirect_stdout
from io import StringIO
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch

from primitive_db.engine import run


def test_crud_scenario():
    """Проверяет CRUD-операции во временной базе данных."""
    original_dir = Path.cwd()

    with TemporaryDirectory() as temp_dir:
        try:
            os.chdir(temp_dir)
            output = StringIO()

            commands = [
                "create_table auto_test name:str age:int",
                'insert into auto_test values ("Anna", 24)',
                'update auto_test set age = 25 where name = "Anna"',
                "select from auto_test",
                "exit",
            ]

            with (
                patch("primitive_db.engine.prompt.string", side_effect=commands),
                redirect_stdout(output),
            ):
                run()

            records = json.loads(
                Path("data/auto_test.json").read_text(encoding="utf-8")
            )

            assert records == [{"ID": 1, "name": "Anna", "age": 25}]

            commands = [
                "delete from auto_test where ID = 1",
                "drop_table auto_test",
                "exit",
            ]

            with (
                patch("primitive_db.engine.prompt.string", side_effect=commands),
                patch("builtins.input", return_value="y"),
                redirect_stdout(output),
            ):
                run()

            assert not Path("data/auto_test.json").exists()
            assert json.loads(Path("db_meta.json").read_text(encoding="utf-8")) == {}

        finally:
            os.chdir(original_dir)


if __name__ == "__main__":
    test_crud_scenario()
    print("CRUD test: PASS")
