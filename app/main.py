from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def read_root() -> dict:
    """
    Root endpoint returning a greeting message.
    
    Returns:
        dict: A dictionary containing a greeting message with key 'message'.
    """
    return {"message": "Hello World"}