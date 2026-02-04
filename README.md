Little backend for a kanban project managment app.

![Gitea Stars](https://img.shields.io/gitea/stars/a-mayb3/Kanban_clone_backend?gitea_url=https%3A%2F%2Fgit.vollex.cc%2F&style=for-the-badge&logo=forgejo&label=Stars%20on%20git.vollex.cc)
![GitHub Repo stars](https://img.shields.io/github/stars/a-mayb3/Kanban_clone_backend?style=for-the-badge&logo=github&label=Stars%20on%20GitHub)

## TechStack
- Python3
- FastAPI + Uvicorn + SQLAlchemy
- SQLite
- git (duh)

![](https://skillicons.dev/icons?i=python,fastapi,sqlite,git)

## How to run
### *nix systems (Linux, MacOS, BSD, etc...)
```bash
git clone --depth=1 https://github.com/a-mayb3/Kanban_clone_backend # or git clone --depth https://git.vollex.cc/a-mayb3/Kanban_clone_backend.git
cd Kanban_clone_backend
python3 -m venv env
source env/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload
```
