import os

from fastapi import FastAPI

from app.api.store import ModelStore

app = FastAPI()  # Add your configuration here

# DO NOT EDIT
app.state.model_store = ModelStore()


if __name__ == '__main__':
    port = os.getenv('PORT', 8080)
    # FIXME: The API should be launched here
