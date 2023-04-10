# syntax=docker/dockerfile:1.4
FROM --platform=$BUILDPLATFORM python:3.10-alpine AS builder

WORKDIR /src
COPY requirements.txt /src
RUN --mount=type=cache,target=/root/.cache/pip \
    pip3 install -r requirements.txt


COPY . .

#FROM builder as dev-envs

RUN <<EOF
apk update
apk add git
apk add zip vim wget curl
EOF


RUN <<EOF
addgroup -S docker
adduser -S --shell /bin/bash --ingroup docker vscode
EOF



#apk add --update alpine-sdk
#apk add gcc wget make zlib zlib-dev openssl openssl-dev
#apk add util-linux pciutils usbutils coreutils binutils findutils grep iproute2
#apk add bash bash-doc bash-completion
#apk add build-base gcc abuild binutils binutils-doc gcc-doc
#apk add --virtual build-dependencies build-base
#EOF
#RUN <<EOF
#wget https://download.httrack.com/cserv.php3?File=httrack.tar.gz -O httrack.tar.gz
#tar -xzvf httrack.tar.gz
#cd httrack-3.49.2
#./configure
#make
#EOF




# install Docker tools (cli, buildx, compose)
COPY --from=gloursdocker/docker / /

CMD ["python3", "server.py"]
