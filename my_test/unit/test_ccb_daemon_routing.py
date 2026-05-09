import importlib.util
from pathlib import Path



def load_ccb_module(repo_root: Path):
    spec = importlib.util.spec_from_file_location(
        'ccb_shim',
        repo_root / 'ccb',
    )
    module = importlib.util.module_from_spec(spec)
    assert spec is not None
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module



def test_ccb_shim_imports_daemon_cli():
    repo_root = Path(__file__).resolve().parents[2]
    ccb = load_ccb_module(repo_root)

    assert hasattr(ccb, 'run_daemon_cli')



def test_ccb_shim_routes_daemon_command(monkeypatch):
    repo_root = Path(__file__).resolve().parents[2]
    ccb = load_ccb_module(repo_root)

    calls = []

    def fake_daemon_cli(argv, *, project_root, stdout, stderr):
        calls.append(
            {
                'argv': argv,
                'project_root': project_root,
            }
        )
        return 0

    monkeypatch.setattr(ccb, 'run_daemon_cli', fake_daemon_cli)
    monkeypatch.setattr(ccb.sys, 'argv', ['ccb', 'daemon', 'status'])

    result = ccb.main()

    assert result == 0
    assert calls == [
        {
            'argv': ['status'],
            'project_root': Path.cwd(),
        }
    ]
