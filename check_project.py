"""Health check + automatic repair.   Run:   python check_project.py

1. Repairs hidden problems at the start of every .py file (extra spaces, BOM) and checks the code is valid.
2. Creates the .env file if it is missing (asks for your MySQL password).
3. Tests the MySQL connection and counts the earthquakes in the table.
It tells you in plain words what to do next.
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
INVISIBLE = " \t\f\u00a0\u200b\ufeff"


def check_python_files() -> bool:
    all_ok = True
    for path in sorted(ROOT.rglob("*.py")):
        if ".venv" in path.parts or "__pycache__" in path.parts:
            continue
        original = path.read_bytes().decode("utf-8-sig", errors="replace")
        lines = original.replace("\r\n", "\n").split("\n")
        if lines and lines[0].strip() and not lines[0].lstrip(INVISIBLE).startswith("#"):
            lines[0] = lines[0].lstrip(INVISIBLE)           # first line must start at the left edge
        fixed = "\n".join(lines)
        rel = path.relative_to(ROOT)
        if fixed != original.replace("\r\n", "\n"):
            path.write_text(fixed, encoding="utf-8")
            print(f"[FIXED] {rel}: removed hidden spaces at the start of the file")
        try:
            compile(fixed, str(path), "exec")
        except SyntaxError as exc:
            all_ok = False
            print(f"[FAIL]  {rel}: line {exc.lineno}: {exc.msg}")
    if all_ok:
        print("[OK]    all Python files are valid")
    return all_ok


def ensure_env_file() -> None:
    env = ROOT / ".env"
    if env.exists():
        print("[OK]    .env file found")
        return
    print("[INFO]  .env file not found - creating it now.")
    password = input("        Type your MySQL root password and press Enter: ").strip()
    env.write_text(f"DB_HOST=localhost\nDB_PORT=3306\nDB_USER=root\nDB_PASSWORD={password}\nDB_NAME=seismic\n",
                   encoding="ascii", errors="ignore")
    print("[OK]    .env file created")


def check_mysql() -> bool:
    try:
        from sqlalchemy import text
        from src.db import get_engine
        with get_engine().connect() as conn:
            rows = conn.execute(text("SELECT COUNT(*) FROM earthquakes")).scalar()
        print(f"[OK]    MySQL connected - {rows:,} earthquakes are in the table")
        return rows > 0
    except ModuleNotFoundError as exc:
        print(f"[FAIL]  a library is missing: {exc.name}  ->  run:  pip install -r requirements.txt")
    except Exception as exc:  # noqa: BLE001
        msg = str(exc)
        print("[FAIL]  MySQL problem:", msg.splitlines()[0][:250])
        if "Access denied" in msg:
            print("        -> wrong password. Delete the .env file, then run this check again.")
        elif "2003" in msg or "Can't connect" in msg:
            print("        -> MySQL is not running. In the terminal run:  Start-Service MySQL80")
        elif "doesn't exist" in msg or "Unknown database" in msg:
            print("        -> the data is not loaded yet. Run:  python run_pipeline.py")
    return False


if __name__ == "__main__":
    print(f"Python {sys.version.split()[0]}")
    files_ok = check_python_files()
    ensure_env_file()
    db_ok = check_mysql()
    try:
        import streamlit
        print(f"[OK]    streamlit {streamlit.__version__}")
    except ModuleNotFoundError:
        print("[FAIL]  streamlit is not installed  ->  run:  pip install -r requirements.txt")
        db_ok = False
    print()
    if files_ok and db_ok:
        print(">>> ALL GOOD. Now start the dashboard with:   streamlit run app/streamlit_app.py")
    else:
        print(">>> Fix the [FAIL] lines above, then run this check again:   python check_project.py")
