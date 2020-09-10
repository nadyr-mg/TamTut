## TamTut

#### Social network with creative ideas based on similar user interests

### Deploy using docker:

Launch (Ctrl+c to stop the containers): 
`docker-compose up`

Launch in background: 
`docker-compose up -d`

Get container logs: 
`docker-compose logs`

Run `bash` inside a container: 
`docker-compose exec web /bin/bash`

Go to PostgreSQL container as postgres user: 
`docker-compose exec -u postgres db /bin/bash`

Connect to the local database inside the container:
`psql -d mydb -U postgres -W testing321`

Stop running containers:
`docker-compose stop`

Stop and remove running containers:
`docker-compose down`

Rebuild images:
`docker-compose build`
