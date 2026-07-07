from invoke import task
import shutil
import sys

@task
def setup(c):
    c.run("python -m venv venv")
    pip = "venv\\Scripts\\pip"
    c.run(f"{pip} install --upgrade pip pip-tools")
    c.run(f"{pip} install -r requirements.lock.txt")

@task
def build_core(c):
    """Собрать Go-ядро"""
    if not shutil.which("go"):
        raise SystemExit("Go не найден в PATH")
    with c.cd("core-go"):
        c.run("go build -o ../manager-python/encoder.exe cmd/encoder/main.go")

@task(pre=[build_core])
def gui(c):
    """Собрать ядро и запустить GUI"""
    python = "venv\\Scripts\\python" if sys.platform == "win32" else "venv/bin/python"
    c.run(f"{python} -m app.entrypoints_gui")

@task
def daemon(c):
    """Запустить демон (для отладки, с консолью)"""
    python = "venv\\Scripts\\python" if sys.platform == "win32" else "venv/bin/python"
    c.run(f"{python} -m app.entrypoints_daemon")

@task(pre=[build_core])
def build_exe(c):
    """Собрать оба .exe через PyInstaller"""
    python = "venv\\Scripts\\python"
    c.run(f"{python} -m PyInstaller packaging/gui.spec --distpath dist/gui")
    c.run(f"{python} -m PyInstaller packaging/daemon.spec --distpath dist/daemon")