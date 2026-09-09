---
marp: true
theme: gaia
paginate: true
---

<style>
  :root {
    /* Slide background, code foreground
       Second color is used for class: invert */
    --color-background: light-dark(#f9f9f9, #0288d1);
  }
</style>

# Docker
<!-- _class: lead -->

Containerizing Services

---

## Our Project

1. Managed with git
2. **Running Docker containers**
3. Orchestrated with Kubernetes
4. Tested in Gitlab
5. Deployed with ArgoCD
6. Monitored with Prometheus and Grafana

---

## Why Containerization?

Modern DevOps projects have many separate components

Each component requires its own libraries and configuration

We wish to deploy, scale, and upgrade each component independently from others

Containerization is one way to allow this

---

## Docker Containers

- Encapsulate application and libraries
- Isolates from rest of system
- Shares kernel with host
- Build on two Linux primitives: **namespaces** and **cgroups**

---

## Docker: Namespaces

Linux namespaces isolate processes in the container from the rest of of the system
- **Process ID:** Processes in the container cannot see those outside
- **Network:** Container has own network stack, IP, ports
- **Mount:** Isolated file system mounts
- **User:** Separate user and group IDs; container root is not host root
- Others, including **UTS**, **IPC**, **cgroup**

---

## Docker: Cgroups

**Control groups** limit the amount of resources processes in a container can consume:
- **CPU**
- **Memory**
- **Disk I/O**
- **Network bandwidth**

---

## Virtual Machines vs. Containers
<!-- _class: lead -->

![center](images/vm-container.svg)

---

## Container Escapes

Shared kernel means flaws in isolation can let container processes escape into host
- CVE-2024-21626 ("Leaky Vessels"): Leaked file descriptor in _runc_
- CVE-2025-23266 ("NVIDIAScape"): LD_PRELOAD injection with NVIDIA container toolkit
- CVE-2026-34040: Bypass authentication in Docker Engine
- CVE-2026-53362, CVE-2026-46242 ("Bad Epoll"), CVE-2026-43499 ("GhostLock"): kernel-level escapes

---

## Docker Elements

**Dockerfile:** Text file describing how to create an image

**Image:** Files containing the filesystem for a new container
- Stored as layers, identified by content hash

**Container:** Running processes, with filesystem from image
- Can be stopped and restarted
- Overlay filesystem to persist changes

---

## Starting a Container

```bash
docker run -it ubuntu:26.04
```

`-i` Keep stdin open, so we can interact with the container
`-t` Allocate a pseudo-TTY, so we get a terminal prompt
`ubuntu` Name of image, here an official image on [hub.docker.com](https://hub.docker.com)
&bull; `user/image-name` for other users of Docker Hub
&bull; `example.com/image-name` for images hosted elsewhere
`:26.04` Image tag, indicating version
&bull; Defaults to `:latest`

---

## Tracking Containers

```bash
docker container list
```
Shows all running containers
&rarr; See stopped containers as well with `-a` argument

Containers are automatically given names
&rarr; Can also specify with `--name` argument to `docker run`

---

## Activity: Named Container

<!-- _class: invert -->

1. Stop the current container (`exit` at command prompt)

2. Create a new container with a memorable name

3. In another terminal, get a list of all containers, both the first container that's stopped and the second one you just started

---

## Accessing Running Containers

Execute commands with a running container with `docker exec`

```bash
docker exec container-name whoami
```
&rarr; Execute the `whoami` command inside `container-name`

```bash
docker exec -it container-name bash
```
&rarr; Start an interactive _bash_ shell inside `container-name`

---

## Managing Containers

Stop the container:
```bash
docker stop container-name
```

Restart a stopped container:
```bash
docker start container-name
```

Delete a container (must be stopped):
```bash
docker rm container-name
```

---

## Discussion: DevSecOps Principles

<!-- _class: invert -->

How do named containers fit into DevSecOps principles?
1. Repeatability and automation
2. Configuration as code
3. Store configuration in version control
4. Declarative, not procedural
5. Livestock, not pets
6. Testing

---

## DevSecOps Principles and Named Containers

1. ~~Repeatability and automation~~
2. ~~Configuration as code~~
3. ~~Store configuration in version control~~
4. Declarative, not procedural
5. ~~Livestock, not pets~~
6. Testing

**Recommendation:** Run containers with `--rm` to delete at exit
$\Rightarrow$ Automate any annoying set up

---

## Using Ephemeral Containers

```bash
docker run -it --rm ubuntu:26.04
```
Container will be deleted when it stops

Any configuration will need to be repeated next time
$\Rightarrow$ Script any configuration steps
$\Rightarrow$ Build custom image already configured

All state stored in container will be lost
$\Rightarrow$ Store important state on docker host; mount onto container

---

## Docker Volumes

Docker **volumes** mount host directory inside container

```bash
mkdir shared  # Create directory to mount
```

Preferred syntax:
```bash
docker run -it --rm --mount type=bind,source=$(pwd)/shared,target=/mnt/volume \
  ubuntu:26.04
```
- `source=` Absolute path on host (error if does not exist)
- `target=` Absolute path in container

<!--
Backslash for line continuation.
There to help us read everything; you can can put it all on one line in the terminal.
-->

---

## Docker Volumes

Legacy syntax:
```bash
docker run -it --rm -v $(pwd)/shared:/mnt/volume ubuntu:26.04
```
- `-v /path/on/host:/path/in/container`
- Creates host path, if doesn't exist
- If host path not absolute, treated as volume name
  - Docker manages storage

---

## Example: Python Web Server

See `project/images/web-service`
- Python web server, implemented in Flask
- Basic visit counter
- LLM chat interface
- Environment managed by _uv_

We don't have these libraries installed in the Codespace

---

## Digression: Lock files

Project dependencies stored in two files
- `pyproject.yaml` lists dependencies author specified
- `uv.lock` lists all packages installed, with specific versions

If lock file exists, _uv_ can **reproduce** the exact environment

Common DevOps practice; see also `package.json`, `package-lock.json` for _npm_ (_Node.js_); `Cargo.toml`, `Cargo.lock` for _Cargo_ (_Rust_)

Also, helps you develop your **Software Bill of Materials (SBOM)**

---

## Build and Run in Docker

Launch a _uv_ image to build and run the webserver

```bash
docker run -it --rm -v $(pwd):/app ghcr.io/astral-sh/uv:python3.14-alpine /bin/sh
```

`-v $(pwd):/app`&mdash;Mount current directory as `/app`
`ghcr.io/astral-sh/uv:python3.14-alpine`&mdash;Container hosted at ghcr.io
`/bin/sh`&mdash;Run this, instead of default command

```bash
cd /app
uv run gunicorn web_service:app --bind 0.0.0.0:8000 --timeout 120
```

---

## Activity: Access Server Within Container
<!-- _class: invert -->

1. Find name of running container

2. Inside running container, execute
   ```bash
   wget -O - http://127.0.0.1:8000/api/visits
   ```

Should get
```
{"visits": 1}
```

<!--
docker container list

docker exec container_name weget -O - http://127.0.0.1:8000/api/visits
OR
docker exec -it container_name /bin/sh
wget -O - http://127.0.0.1:8000/api/visits
-->

---

## Exposing Ports

Expose port in container to host

```bash
docker run -it --rm -v $(pwd):/app -p 8000:8000 \
    ghcr.io/astral-sh/uv:python3.14-alpine /bin/sh
```
`-p 8000:8000`&mdash;Connect port 8000 on host to port 8000 in container

On host, test with
```bash
curl http://localhost:8000/api/visits
```

---

## Codespaces Forwards Ports

Codespaces should notice the open port, set up port forwarding

See the _Ports_ pane next to _Terminal_

---

## Cleanup

1. Stop running container

2. Delete `.venv` directory that was created
   ```bash
   rm -rf .venv
   ```

---

## Dockerfile

Want to automate building and running our service

`Dockerfile` is text file describing how to build a Docker image

---

## Dockerfile

Create file named `Dockerfile`:

```Dockerfile
FROM ghcr.io/astral-sh/uv:python3.14-alpine

ENV UV_COMPILE_BYTECODE=1
ENV UV_LINK_MODE=copy

WORKDIR /app

COPY . /app

CMD ["sh", "-c", \
     "uv run gunicorn web_service:app --bind 0.0.0.0:8000 --timeout 120"]
```

<!--
Backslash for line continuation
Trying to make it readable here, but can be on one line in actual Dockerfile.
-->

---

## Build Custom Image

Build image with `docker build` command:
```bash
docker build . -t web-service
```
`.` Build current directory
`-t web-service` Name the image _web-service_

See local Docker images:
```bash
docker image list
```

---

## Run Custom Image

```bash
docker run --rm -p 8000:8000 web-service
```
Just specify our local image instead of a remote one

Web service should be available on port 8000

---

## Activity: Visitor Count on Volume

<!-- _class: invert -->

The visitor count has been resetting each time we start a container

The service stores the count in `/var/lib/web-service/visits.txt`

1. Run the container with a volume mounted to host this file

2. See that the count is maintained when you stop and restart the container.

<!--
mkdir count

docker run --rm -v $(pwd)/count:/var/lib/web-service -p 8000:8000 web-service
-->

---

## Multi-Stage Builds

Build process often requires tooling not necessary for production
- Here, the _uv_ system
- Increases container size
- More components mean more vulnerabilities

**Multi-stage builds** do build in one image
Then copy relevant files into a second image

---

## Multi-Stage Dockerfile (pt. 1)

```Dockerfile
# Builder stage
FROM ghcr.io/astral-sh/uv:python3.14-alpine AS builder

ENV UV_COMPILE_BYTECODE=1
ENV UV_LINK_MODE=copy

WORKDIR /app

COPY . /app

RUN uv sync --frozen --no-dev --no-editable
```
_&mdash;Continues&rarr;_

---

## Multi-Stage Dockerfile (pt. 2)

_&larr;Continued&mdash;_

```Dockerfile
# Final stage
FROM python:3.14-alpine

WORKDIR /app

COPY --from=builder /app/.venv /app/.venv

ENV PATH="/app/.venv/bin:$PATH"

CMD ["sh", "-c", "gunicorn web_service:app --bind 0.0.0.0:8000 --timeout 120"]
```

---

## Multi-Stage Dockerfile

Build and run as before:
```bash
docker build . -t web-service-staged
docker run --rm -v $(pwd)/count:/var/lib/web-service -p 8000:8000 \
    web-service-staged
```

Note difference in image size reported by `docker image list`

---

## Security and Reproducibility

Docker image tags are controlled by provider, are mutable

Can, and often are, updated with bugfixes and upgrades
&rarr; `:latest` is always updated!

Lock down version with image **digest**, a SHA-256 hash of image contents

```bash
docker images --digests
```
Also available on [Docker Hub](https://hub.docker.com/layers/library/python/3.14-alpine/images/sha256-ca6bc805db937801472d52675e31565a9fef0535962a86a2593b1c2b1b323a86)

---

## Docker Image Digests

Use instead of tag in specifying image

```bash
docker run python@sha256:c6ead2...cb96fc
```

```Dockerfile
FROM python@sha256:c6ead2...cb96fc

...
```

A digest specifies one unchanging image &hellip;

&hellip; but it can disappear from the source repository.

<!--
Discussion: Should we specify tags or digests
Digests: Ensure reproducibility.  Slow supply chain attacks
Tags: May get bugfixes, upgrades.

Note that source repository can delete an image.  Having its
digest is not enough to recreate it.  So probably a good idea
to copy images you need to your own repository.  (Details later.)
-->

---

## Environmental Variables

Configuration often accomplished via environmental variables

Defaults can be specified in Dockerfile with `ENV` command:
```Dockerfile
ENV variable=value
```

Defaults overridden when launch container with `-e` argument:
```bash
docker run -e variable=newvalue ...
```

---

## Configure Service via Variables

_&larr;Continued&mdash;_
```Dockerfile

COPY --from=builder /app/.venv /app/.venv

ENV PATH="/app/.venv/bin:$PATH"
ENV PORT=8000
ENV VISIT_COUNTER_FILE="/var/lib/web-service/visits.txt"
ENV OLLAMA_URL="http://localhost:11434"
ENV OLLAMA_MODEL="qwen3:0.6b"

CMD ["sh", "-c", \
     "gunicorn web_service:app --bind 0.0.0.0:$PORT --timeout 120"]
```

---

## Change Port via Variable

```bash
docker build . -t web-service-staged
docker run --rm -v $(pwd)/count:/var/lib/web-service \
    -e PORT=3000 -p 8000:3000 web-service-staged
```

`-e PORT=3000` sets the variable _PORT_ to "3000"
`Dockerfile` uses `$PORT` to set the port _gunicorn_ serves at
`-p 8000:3000` forwards local port 8000 to container port 3000
$\Rightarrow$ Still shows up on port 8000 in Codespaces

---

## Running as User Other than _root_

- Many containers run as container root user
  - Not designed for multi-user operation
- Many container escapes require root access within container
  - Running as non-root user adds an additional hurdle

Best practice for containers running public services: Run service as a non-root user in container

---

## Creating Another User (pt. 1)

```Dockerfile
...
FROM python:3.14-alpine

ARG USER_UID=1000
ARG USER_GID=1000
RUN addgroup -g $USER_GID -S appuser && \
    adduser -u $USER_UID -S appuser -G appuser

WORKDIR /app

COPY --from=builder --chown=appuser:appuser /app/.venv /app/.venv
...
```

Creates user _appuser_; switch ownership of copied files to _appuser_

<!--
This specifies the uid and gid of the added user.  This may be necessary
to make bind mounts work; more on that later.
-->

---

## Creating Another User (pt. 2)

```Dockerfile
...
ENV OLLAMA_MODEL="qwen3:0.6b"

RUN mkdir $(dirname $VISIT_COUNTER_FILE) && \
    chown appuser:appuser $(dirname $VISIT_COUNTER_FILE)

USER appuser

CMD ["sh", "-c", \
     "gunicorn web_service:app --bind 0.0.0.0:$PORT --timeout 120"]
```

Ensure _appuser_ can write to (default) `$VISIT_COUNTER_FILE`

Switch to _appuser_ to run the Python service

---

## User IDs and Bind Mounts

- File owner IDs are not translated across the container boundary (‽)
  - Not a problem for the root user
  - Can be a problem for non-root users
- Here, we set the _appuser_ id to 1000, same as host user owning files
  - `ARG` can be set at **build** time:
    ```Docker
    docker build --build-arg USER_UID=$(id -u) ...
    ```
  - This cannot be adjusted at **run** time

---

## User IDs and Bind Mounts

Other solutions:
- Run docker container as a different user:
  ```bash
  docker run --user $(id -u):$(id -g) ...
  ```
  - Not baked into image
- Add **entrypoint** that creates new user, _chown_, and run application as new user
- Kubernetes will handle ownership of mounts itself
