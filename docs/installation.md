## Installation

### docker

Web app hosted on localhost 8008/tcp:
```bash
# start the service
docker compose up -d

# close everything
docker compose down

# start debug version, backend exposed without nginx as the frontend 
docker compose -f compose_debug_env.yaml up -d

# stop debug version
docker compose -f compose_debug_env.yaml down

```


<br />

### Python's virtualenv

A mongodb hosted on port 27017 is required, then create the virtualenv and install requirements as follows:

```bash
rm -rf object_virtualenv
mkdir object_virtualenv 
virtualenv --python=python3 object_virtualenv
source object_virtualenv/bin/activate

cd src
python -m pip install -r requirements.txt
```

Spawn the service:
```bash
# python server.py --host <address-listening> --mongo_ip <mongodb-address> --debug
python server.py --host 127.0.0.1 --mongo_ip 127.0.0.1 --debug
```

 - NOTE: if you reset the db then the web service should be restarted and staging folder (default: /tmp/db_capa) should be cleared of the previously created folder


