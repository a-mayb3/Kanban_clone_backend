Little backend for a kanban project managment app.

## TechStack
- Python3
- FastAPI + Uvicorn
- SQLite + SQLAlchemy
- git + GitHub (duh)

![](https://skillicons.dev/icons?i=python,fastapi,sqlite,git,github)

## How to run
### *nix systems (Linux, MacOS, BSD, etc...)
```bash
git clone --depth=1 https://github.com/a-mayb3/Kanban_clone_backend
cd Kanban_clone_backend
python3 -m venv env
source env/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload
```
