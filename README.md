# Rest API workshop

This workshop should should take around 1 hour to complete.

### Prerequisites

Before starting this workshop make sure that you have Python >= 3.10 installed. Next install the
packages you will be using by running `pip install -r requirements.txt`.

Unit tests have been written to test all the endpoints you will implement throughout the workshop. Check that you are able
to run the tests by running `./scripts/run_tests.sh`. You should see all 21 tests fail. You should use `./scripts/start_api.sh`
to start the API once you have implemented `app/main.py` correctly.

### Introduction

We will be implementing a simple API using FastAPI using the spec provided in `workshop-v1.0.yaml`. You should begin by 
familiarising yourself with the API spec and the project structure using the diagram provided below.

```
restapi-workshop 
│
└───app
│   │   main.py  <-- use this to launch the API
│   │
│   └───api
│       │
│       └───errors <-- Used to store error models
│       │   │   error_response.py <-- Contains an ABC for an error model
│       │
│       └───operations <-- Used implement the handlers for each endpoint here
│       │   │   post_models.py <-- An incomplete implementation of POST /models
│       │
│       └───resources <-- Used to store resource definitions
│       │   │   model.py <-- An incomplete definition of a Model
│       │   │   results.py <-- An incomplete definition of a ResultItem
│       │   │   status.py <-- An incomplete definition of a Status
│ 
└───store
│   │   model_store.py <-- An in memory model store with some additional useful functionality
│ 
└───test
│   │   test_*.py  <-- Unit tests for each endpoint that you will implement
│
└───api
   
```

You are free to modify any of the code provided for you, except lines that have `DO NOT EDIT` comments above
them - please do not modify these under any circumstances. All the code provided has accompanying unit tests so should you
change the code, you may also need to update the tests. 

**Note:** Some of the code provided will not work until you have implemented the correct resource definitions.

### Tasks

#### Task 1

To check that everything is working correctly, implement `main.py` to launch the API, then run `./scripts/start_api.sh` 
to check that the API runs without any errors. Once you have confirmed this, move on to the next task.


#### Task 2

Implement the get `/healthz` endpoint using the definition provided in the API spec. Once you have done this you can check
that your implementation is correct by running the tests for this endpoint using `python -m unittest app/test/test_get_healthz.py`.
Once all tests pass, move on to the next task.

#### Task 3

Now that you have a basic API with a single endpoint working correctly, you should now implement all the other endpoints
and resource definitions from the API spec in any order you like. You should also address any `FIXME` comments in the code
provided. 

When implementing `GET /models/{model_id}/results` you should ensure that it is not possible to retrieve results for any
model that is not in the `completed` state.


#### Task 4

Once you have completed an implementation of all endpoints and all tests pass, we will introduce some randomness to the API
to make the API slightly less deterministic. Implement the following the rules:

- `GET /models/{model_id}` return an internal server error for approximately 1% of requests.
- `DELETE /models/{model_id}` return an internal server error for approximately 2% of requests.
- `POST /models` should send a bad request response if `airbus.com` is in the `data_source` URL. The error message should
inform the client that the data source could not be reached.


#### Tips

Below you will find some useful tips to help you with the workshop.

#### Accessing the ModelStore

The `ModelStore` is a global in-memory store for models and results. It is instantiated when the API starts up ([here](https://github.com/james-zafar/restapi-workshop/blob/main/app/main.py#L10)) 
and can be accessed in any endpoint by adding an argument to any handler function which accepts a Request object which 
stores a reference to the app. An example is provided below

```python
from fastapi import Request

@router.get('/example')
def get_example(request: Request) -> None:
    my_model = request.app.state.model_store['model_id']  # Retrieve a model
    request.app.state.model_store['model_id'] = 'A model'  # Create a new model
```

#### Custom responses

If you need to add additional information to a response, for example headers then you should use `fastapi.responses.JSONResponse`.
An example of using JSONResponse to send headers as part of a response is provided below.

```python
from fastapi.responses import JSONResponse

@router.get('/example')
def get_example() -> JSONResponse:
    response_content = {'an': 'example'}
    headers = {  # Headers should be a dictionary
        'Content-Language': 'en-US'
    }
    return JSONResponse(content=response_content, headers=headers, status_code=200)
```