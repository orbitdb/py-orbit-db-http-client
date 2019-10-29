FROM python:latest

WORKDIR /py-orbit-db-http-client
RUN curl -L https://github.com/orbitdb/py-orbit-db-http-client/tarball/develop | tar -xz --strip-components 1 \
 && pip install .