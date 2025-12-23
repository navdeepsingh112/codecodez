

from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def read_root() -> dict:
    """
    Root endpoint returning a welcome message.

    Returns:
        dict: A dictionary containing a welcome message.
    """
    return {"message": "Welcome to the FastAPI application!"}