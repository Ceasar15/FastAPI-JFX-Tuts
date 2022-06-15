from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI

from book import api


app = FastAPI()

# cors
origins = ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# routes
app.include_router(api.router)


@app.get("/",)
def index():
    return {
        "hello": "world",
    }
