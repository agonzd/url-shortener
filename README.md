# Test the app
LINK TODO


## How to run locally
To run this project, you need Docker Compose. For that, I recommend using Docker Desktop for an easier setup.

For the first time running the project, use the following command to build and start the containers: `docker-compose up --build`

For subsequent uses, you can simply use `docker-compose up`

Once the containers are running, you can access the app at: http://localhost:3000

To run the tests, follow these steps:
1. `docker-compose up -d test-db backend` -> This starts the backend and test database
2. `docker-compose exec backend pytest -v` -> This runs the tests
3. `docker-compose down` -> After finishing you can clean up the containers.


### Assumptions
- If a URL suffix has expired and a user wants it, the previous entry is deleted and a new one is created with the entered URL.
- You can still see the information of an expired URL.


### Challenges or difficulties 
 - I tried to use Express.js as the backend at first, but I had some problems trying to dockerize the app, so I changed to FastAPI.
 - I have never tested with FastAPI and it gave my a lot of difficulties.