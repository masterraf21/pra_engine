import uvicorn
from src.config import get_settings

if __name__ == "__main__":
    env = get_settings()

    reload = env.environment == "dev"
    uvicorn.run("src.main:app", host="0.0.0.0", port=env.port, reload=reload, log_config="./log_config.yaml")
