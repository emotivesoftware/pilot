from __future__ import annotations

from pathlib import Path
from unittest.mock import patch

import pytest

from pilot.config import BenchConfig
from pilot.managers.processes.local import ProcessManager
from tests.pilot.core.test_workspace import make_linked_bench, make_repo


def get_dev_process_names(bench) -> set[str]:
    with patch("pilot.core.app.node_packages.shutil.which", side_effect=lambda name, **_: name):
        return {pd.name for pd in ProcessManager(bench)._process_definitions() if pd.name.endswith("-dev")}


@pytest.mark.parametrize(
    ("setting", "expected"),
    [(None, {"gameplan-dev"}), ([], set()), (["gameplan"], {"gameplan-dev"}), (["other"], set())],
)
def test_app_dev_servers_selects_linked_dev_processes(tmp_path: Path, setting, expected) -> None:
    bench = make_linked_bench(tmp_path / "bench", make_repo(tmp_path / "src" / "gameplan"))
    bench.config.app_dev_servers = setting

    assert get_dev_process_names(bench) == expected


def test_app_dev_servers_round_trips_through_bench_toml(tmp_path: Path) -> None:
    bench = make_linked_bench(tmp_path / "bench", make_repo(tmp_path / "src" / "gameplan"))
    bench.config.app_dev_servers = []
    bench.config.write(bench.path)

    assert "app_dev_servers = []" in (bench.path / "bench.toml").read_text()
    assert BenchConfig.read(bench.path).app_dev_servers == []


def test_unset_app_dev_servers_stays_out_of_bench_toml(tmp_path: Path) -> None:
    bench = make_linked_bench(tmp_path / "bench", make_repo(tmp_path / "src" / "gameplan"))
    bench.config.write(bench.path)

    assert "app_dev_servers =" not in (bench.path / "bench.toml").read_text()
    assert BenchConfig.read(bench.path).app_dev_servers is None
