import importlib.util
from importlib.machinery import SourceFileLoader
from pathlib import Path



def load_ccb_module(repo_root: Path):
    ccb_path = repo_root / 'ccb'
    if not ccb_path.exists():
        raise FileNotFoundError(f'ccb script not found at {ccb_path}')

    loader = SourceFileLoader('ccb_shim', str(ccb_path))
    spec = importlib.util.spec_from_file_location('ccb_shim', str(ccb_path), loader=loader)
    module = importlib.util.module_from_spec(spec)
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
