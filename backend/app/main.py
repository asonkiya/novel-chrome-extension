from fastapi import FastAPI
from app.api.routes import all_routers

app = FastAPI(title="Novel Translator API")

for r in all_routers:
    app.include_router(r)
