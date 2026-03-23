from backend.app.core.config import AppConfig
from backend.app.presentation.web import serve


if __name__ == "__main__":
    serve(AppConfig.from_env())
