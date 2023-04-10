
## Refs

 - Guida docker
    * https://github.com/docker/awesome-compose/tree/master/nginx-flask-mongo
    * https://serverfault.com/questions/1067566/docker-compose-is-not-a-docker-command-how-to-use-the-alias-docker-compos

 - Guida flask template
    * https://www.digitalocean.com/community/tutorials/how-to-make-a-web-application-using-flask-in-python-3
 
 - Guida mongo python
    * https://www.w3schools.com/python/python_mongodb_find.asp

 - Capa FLARE fireeye
    * https://github.com/mandiant/capa


<br />

----

## Istruzioni

 - Prima fai deploy con docker [docker-deploy](#docker-deploy)
 - Oppure soluzione con virtualenv, esempio [virtualenv-python](#virtualenv-python)


<br />

----

### docker deploy

```
$ docker compose up -d
Creating network "nginx-flask-mongo_default" with the default driver
Pulling mongo (mongo:)...
latest: Pulling from library/mongo
423ae2b273f4: Pull complete
...
...
Status: Downloaded newer image for nginx:latest
Creating nginx-flask-mongo_mongo_1 ... done
Creating nginx-flask-mongo_backend_1 ... done
Creating nginx-flask-mongo_web_1     ... done

```

### Expected result

Listing containers must show three containers running and the port mapping as below:
```
$ docker ps
CONTAINER ID        IMAGE                        COMMAND                  CREATED             STATUS              PORTS                  NAMES
a0f4ebe686ff        nginx                       "/bin/bash -c 'envsu…"   About a minute ago   Up About a minute   0.0.0.0:80->80/tcp     nginx-flask-mongo_web_1
dba87a080821        nginx-flask-mongo_backend   "./server.py"            About a minute ago   Up About a minute                          nginx-flask-mongo_backend_1
d7eea5481c77        mongo                       "docker-entrypoint.s…"   About a minute ago   Up About a minute   27017/tcp              nginx-flask-mongo_mongo_1
```

top and remove the containers
```
$ docker compose down
```

<br />

----

### virtualenv python

 - Tested on ubuntu 20.04
 - Nota: dobbiamo esporre mongodb in locale su porta 27017, oppure lasciamo docker di prima accesi e forwardiamo traffico così 127.0.0.1:27017 -> 27017:nginx -> 27017:nginx-flask-mongo_backend


```bash
rm -rf object_virtualenv
mkdir object_virtualenv 
virtualenv --python=python3 object_virtualenv
source object_virtualenv/bin/activate

# some issue with install sorry, instead you need to install manually packages
cd src
python -m pip install -r requirements.txt

python server.py --host 127.0.0.1 --mongo_ip 127.0.0.1 --debug
```


