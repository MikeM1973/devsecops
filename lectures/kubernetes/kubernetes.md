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
  .highlighted-line {
    display: block;
    background-color: #ffaa0040;
    margin: 0 -6px;
    padding: 0 6px;
  }
  div.columns {
    display: flex;
    gap: 1em;
  }
  div.columns > div {
    flex: 1;
  }
</style>

# Kubernetes
<!-- _class: lead -->

Orchestrating Containers

---

## Our Project

1. Managed with git
2. Running Docker containers
3. **Orchestrated with Kubernetes**
4. Tested in Gitlab
5. Deployed with ArgoCD
6. Monitored with Prometheus and Grafana

---

## Orchestrating Containers on a Cluster

**Situation:** Have many containers and several machines

**Goal:** Get all of the containers running somewhere
- Making sure they are actually running
- Restarting them if they crash
- Facilitating communication between them
- Exposing external services to the world

---

## Kubernetes (K8s)

Container orchestration in a cluster

Various **kinds** of resources declared in YAML files
&rarr; Kubernetes tries to update cluster to match desired state

Grew out of internal Google project ("Borg")
$\Rightarrow$ Many features and capabilities
$\Rightarrow$ Most teams won't need most features

---

## Understanding Kubernetes

- Kubernetes is a huge project&mdash;we can't cover it all
- **Goals:**
  - Understand basic concepts of K8s
  - Gain familiarity with the K8s CLI
  - Deploy a few common elements on a K8s cluster
- **Non-goals:**
  - Knowing all K8s kinds
  - Knowing all configuration options
- **You know enough to learn what you need when you need it**

---

## K8s Cluster Architecture

![bg contain](images/components-of-kubernetes.svg)

<!-- _footer: "From [Kubernetes Documentation](https://kubernetes.io/docs/concepts/overview/components/), CC BY 4.0" -->

<!--
Control plane generally 3 machines.
Odd number for Raft consensus algorithm

On each node:
- kubelet: Talks to API server, gets containers to run
- kube-proxy: Handles networking
- container layer: often containerd
-->

---

## Minikube

Implementation of Kubernetes designed to run on a single node

Runs entirely within a VM or docker container

Often used for local development and testing

---

## Activity: Start Minikube

<!-- _class: invert -->

Start Minikube with:
```bash
minikube start
```
This will take a few  minutes

Once it's up, you should see both a client and server version from:
```bash
kubectl version
```

---

## YAML Configuration in K8s

<style scoped>
  table {
    width: 100%
  }
</style>


- Superset of JSON, designed to be human-readable
- Full language is (overly) complex

| Atomic | Types | Composite | Types |
|---:|:---|---:|:---|
| number | `12.345` | sequence | `[1, 2, 3, 4, 5]` |
| string | `"hello"` | mapping | `{"key": "value"}` |
| boolean | `true` and `false` | | |
| null |`null`| | |

---

## YAML Block Syntax

Alternative syntax for sequences and mappings relies on whitespace

<div class="columns">
<div>

#### Block Syntax
```yaml
# YAML supports comments
key: "value"
nested:
  subkey: value
  list:
    - "Item 1"
    - "Item 2"
```
String quoting optional, unless it causes ambiguity

</div>
<div>

#### Flow Syntax (JSON)

```json
{
  "key": "value",
  "nested": {
    "subkey": "value",
    "list": [
      "Item 1",
      "Item 2"
    ]
  }
}
```

</div>
</div>

<!--
String quoting not required in either syntax, generally.

I can never remember when quotes are needed, so I tend to include them if there's anything other than alphanumerics in a string.  Technically, don't need quotes around "Item 1".

Also a gazillion syntaxes for multi-line strings.
-->

---

## K8s Pods: Smallest Unit of Compute

- One or more docker containers, always deployed together
  - Shared network namespace (access others on localhost)
  - Shared storage volumes
- Generally one main container
  - May have a **sidecar**: auxiliary container for logs, proxy, _etc_.
- Created and destroyed as needed
  - _Livestock, not pets_

---

## Pod Definition

<div class="columns">
<div>

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: web-pod
  labels:
    app: web-service
spec:
  containers:
    - name: web-container
      image: web-service:latest
      imagePullPolicy: Never
      ports:
        - containerPort: 8000
          name: "http"
```
</div>
<div>

Create a new file `project/services/pod.yaml` with these contents
</div>
</div>

---

## Pod Definition: `kind`

<div class="columns">
<div>

```yaml {2}
apiVersion: v1
kind: Pod
metadata:
  name: web-pod
  labels:
    app: web-service
spec:
  containers:
    - name: web-container
      image: web-service:latest
      imagePullPolicy: Never
      ports:
        - containerPort: 8000
          name: "http"
```
</div>
<div>

The _kind_ specifies the type of resource to be created
</div>
</div>

---

## Pod Definition: `apiVersion`

<div class="columns">
<div>

```yaml {1}
apiVersion: v1
kind: Pod
metadata:
  name: web-pod
  labels:
    app: web-service
spec:
  containers:
    - name: web-container
      image: web-service:latest
      imagePullPolicy: Never
      ports:
        - containerPort: 8000
          name: "http"
```
</div>
<div>

Kubernetes kinds are versioned

New versions can been released without breaking old deploys

Mostly see in _beta_ versions of new kinds
</div>
</div>

---

## Pod Definition: Identifiers

<div class="columns">
<div>

```yaml {4,6,9}
apiVersion: v1
kind: Pod
metadata:
  name: web-pod
  labels:
    app: web-service
spec:
  containers:
    - name: web-container
      image: web-service:latest
      imagePullPolicy: Never
      ports:
        - containerPort: 8000
          name: "http"
```
</div>
<div>

`metadata.name`: Identifier for the pod

`metadata.labels.app`: Associates a pod with a **service**
(We'll see this later)

`spec.containers[*].name`: Identifies a container within a pod (required, but superfluous for one-container pod)
</div>
</div>

---

## Pod Definition: Container Image

<div class="columns">
<div>

```yaml {10-11}
apiVersion: v1
kind: Pod
metadata:
  name: web-pod
  labels:
    app: web-service
spec:
  containers:
    - name: web-container
      image: web-service:latest
      imagePullPolicy: Never
      ports:
        - containerPort: 8000
          name: "http"
```
</div>
<div>

Container image on Docker Hub or other registry

To use a local image in minikube, run:
```bash
minikube image load web-service:latest
```

`imagePullPolicy: Never`: Don't even try to pull the image from Docker Hub
</div>
</div>

---

## Pod Definition: Network Ports

<div class="columns">
<div>

```yaml {12-14}
apiVersion: v1
kind: Pod
metadata:
  name: web-pod
  labels:
    app: web-service
spec:
  containers:
    - name: web-container
      image: web-service:latest
      imagePullPolicy: Never
      ports:
        - containerPort: 8000
          name: "http"
```
</div>
<div>

Specify which ports should be open for connections

`name` can be used on other objects to reference the port
</div>
</div>

---

## Launching a Pod

From the `project/services` directory, run:
```bash
kubectl apply -f pod.yaml
```

Check that it has come up with:
```bash
kubectl get pods
```

Can add pod name to limit to specific pod

**Note:** `kubectl get` and similar commands will work with all K8s _kinds_

<!--
Point out that pod's name came from the yaml file
-->

---

## Examining a Pod

Add `-o yaml` to _get_ to see a detailed configuration:
```bash
kubectl get pod -o yaml web-pod
```

The _describe_ command gives detailed information about the state:
```bash
kubectl describe pod web-pod
```

The _logs_ command show application logs:
```bash
kubectl logs web-pod
```

<!--
Not many logs yet, but can check back after making some requests
-->

---

## Debugging Technique: `exec` into Pod

The _exec_ command will run a process inside an existing pod

To get a terminal in our _web-pod_:
```bash
kubectl exec -it web-pod -- /bin/sh
```
Similar options to `docker exec`

The `--` separates the command (and its options) from options to `kubectl exec`

---

## Connecting to a Server in a Pod

With a shell in a pod, we can access the server on localhost:
```bash
wget -O - http://127.0.0.1:8000/api/visits  # From within web-pod ONLY
```

---

## Port Forwarding to a Pod

Forward this port to your local machine (where `kubectl` is running):
```bash
kubectl port-forward pod/web-pod http
```
`http` is `ports[*].name` in configuration
&rarr; Can use port numbers instead
&rarr; Uses same port locally by default; change with `3000:http`, _e.g._

Now, connect to local machine:
```bash
curl http://localhost:8000/api/visits  # On development machine
```

<!--
Also available with Codespaces ports
-->

---

## Deleting a Pod

Pod can be deleted with:
```bash
kubectl delete pod web-pod
```

&hellip; and created anew with:
```bash
kubectl apply -f pod.yaml
```

Note that this creates a new container
$\Rightarrow$ Visit count gets reset

<!--
Question: How did we solve this in Docker?
=> Volumes
-->

---

## Persistent Volumes

**Persistent Volumes** are storage available on the cluster
- Created by cluster administrator
- An instance of a **Storage Class**
  - Local to cluster, or a cloud service
  - Each cloud provider has its own options

Applications request a persistent volume with a **Persistent Volume Claim**

---

## Persistent Volume Claim (PVC)

<div class="columns">
<div>

```yaml {4}
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: web-pvc
spec:
  storageClassName: standard
  accessModes:
    - ReadWriteOnce
  resources:
    requests:
      storage: 10Mi
```
</div>
<div>

Create a new file: `project/services/pvc.yaml`

`metadata.name` is arbitrary
</div>
</div>

---

## Persistent Volume Claim: Storage Class

<div class="columns">
<div>

```yaml {6}
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: web-pvc
spec:
  storageClassName: standard
  accessModes:
    - ReadWriteOnce
  resources:
    requests:
      storage: 10Mi
```
</div>
<div>

`spec.storageClassName` must be available on the cluster

To see available classes:
```bash
kubectl get storageclass
```

_default_ class used if not specified
</div>
</div>

---

## Persistent Volume Claim: Access Modes

<div class="columns">
<div>

```yaml {7-8}
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: web-pvc
spec:
  storageClassName: standard
  accessModes:
    - ReadWriteOnce
  resources:
    requests:
      storage: 10Mi
```
</div>
<div>

- `ReadWriteOnce`
  - Connected to single node with read/write capability
  - Supported by most classes
- `ReadOnlyMany`
  - Multiple nodes, read-only
  - Many classes support
- `ReadWriteMany`
  - Only select classes
</div>
</div>

<!--
ReadWriteMany requires a network or distributed file system.
Standard block storage can't support it.
-->

---

## Persistent Volume Claim: Resource Request

<div class="columns">
<div>

```yaml {9-11}
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: web-pvc
spec:
  storageClassName: standard
  accessModes:
    - ReadWriteOnce
  resources:
    requests:
      storage: 10Mi
```
</div>
<div>

Amount of storage available on the volume
</div>
</div>

---

## Creating a Persistent Volume

```bash
kubectl apply -f pvc.yaml
```

See the claim:
```bash
kubectl get pvc
```

See the volume that got created:
```bash
kubectl get pv
```

<!--
Note that "persistentvolumeclaim and persistentvolume also work.
Most kinds have abbreviations that work.
-->

---

## Mounting the Volume on the Pod

<div class="columns">
<div>

```yaml {6-12}
...
spec:
  containers:
    - name: web-container
      ...
      volumeMounts:
        - mountPath: /var/lib/web-service/
          name: visits-volume
  volumes:
    - name: visits-volume
      persistentVolumeClaim:
        claimName: web-pvc
```
</div>
<div>

Edit `project/services/pod.yaml`

Add these lines to the bottom of the file
</div>
</div>

---

## Mounting the Volume on the Pod

<div class="columns">
<div>

```yaml {11-12}
...
spec:
  containers:
    - name: web-container
      ...
      volumeMounts:
        - mountPath: /var/lib/web-service/
          name: visits-volume
  volumes:
    - name: visits-volume
      persistentVolumeClaim:
        claimName: web-pvc
```
</div>
<div>

Reference the volume associated with the claim we just made
</div>
</div>

---

## Mounting the Volume on the Pod

<div class="columns">
<div>

```yaml {8,10}
...
spec:
  containers:
    - name: web-container
      ...
      volumeMounts:
        - mountPath: /var/lib/web-service/
          name: visits-volume
  volumes:
    - name: visits-volume
      persistentVolumeClaim:
        claimName: web-pvc
```
</div>
<div>

These names must match
</div>
</div>

---

## Mounting the Volume on the Pod

<div class="columns">
<div>

```yaml {7}
...
spec:
  containers:
    - name: web-container
      ...
      volumeMounts:
        - mountPath: /var/lib/web-service/
          name: visits-volume
  volumes:
    - name: visits-volume
      persistentVolumeClaim:
        claimName: web-pvc
```
</div>
<div>

Mount point for this volume in container
</div>
</div>

---

## Multiple Documents in One File

Multiple YAML documents can be stored in the same file

Separate with `---` on its own line

`kubectl apply -f` will process all documents in a file

$\Rightarrow$ Keep related components in the same file

---

## Activity: Pod and PVC Together

<!-- _class: invert -->

1. Create a new YAML file in `project/services`
2. Copy in both the contents from `pod.yaml` and `pvc.yaml`, separated by a line containing `---`
3. Use `kubectl apply -f` on this file
4. What do you notice happens?

<!--
`kubectl apply` takes a diff between the desired state in the file and the actual
state of the cluster.  If they are the same, it doesn't do anything.  If they are
different, it tries to update the cluster state.

This is limited with pods; we'll see it much cleaner with other elements.
-->

---

## Kubernetes Workloads

We shouldn't be managing pods directly (_Livestock, not pets_)
We should describe what's required, and let K8s create the pods

- **Deployment:** Ensure a given number of a pod are running
  - Deployment pods are interchangeable
  - Good for stateless applications (_e.g._ web servers)
- **StatefulSet:** Identical pods, but distinct identities
  - Persistent volumes can be attached to an identity
  - Good for stateful applications (_e.g._ databases)

---

## Additional K8s Workloads

- **ReplicaSet:** Used under the hood by Deployments
- **DaemonSet:** Ensures one pod per node
  - Often used for cluster services (_e.g._ networking)
- **Job:** Pods that run a task to completion, then exit
- **CronJob:** Run a Job periodically

<!--
You are less likely to need these, but you might encounter them in the wild.
-->

---

## Creating a Deployment

<div class="columns">
<div>

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: web-deployment
  namespace: default
  labels:
    app: web-service
spec:
  selector:
    matchLabels:
      app: web-service
  replicas: 1
  template:
```
</div>
<div>

Create a new file `project/services/web-service.yaml` with this contents
</div>
</div>

---

## Specifying the pods

<div class="columns">
<div>

```yaml {12-13}
apiVersion: apps/v1
kind: Deployment
metadata:
  name: web-deployment
  namespace: default
  labels:
    app: web-service
spec:
  selector:
    matchLabels:
      app: web-service
  replicas: 1
  template:
```
</div>
<div>

The Deployment with make `replica` copies of the pod described in `template`

Paste the `metadata` and `spec` mappings from the Pod definition below.  Indent it twice.

Remove `metadata.name` and the persistent volume configuration
</div>
</div>

<!--
Next slide to show what the whole file should look like
-->

---

## Specifying the pods

<div class="columns">
<div>

```yaml {10-11}
apiVersion: apps/v1
kind: Deployment
metadata:
  name: web-deployment
  namespace: dso-project
  labels:
    app: web-service
spec:
  selector:
    matchLabels:
      app: web-service
  replicas: 1
  template:
```
</div>
<div>

```yaml {4-5}
# File continues...
    metadata:
      name: web-pod
      labels:
        app: web-service
    spec:
      containers:
        - name: web-container
          image: web-service:latest
          imagePullPolicy: Never
          ports:
            - containerPort: 8000
              name: "http"
```

</div>
</div>

<!--
The labels on the pod are used by the selector to identify the pods
that are port of the Deployment
-->

---

## Namespaces

<div class="columns">
<div>

```yaml {5}
apiVersion: apps/v1
kind: Deployment
metadata:
  name: web-deployment
  namespace: dso-project
  labels:
    app: web-service
spec:
  selector:
    matchLabels:
      app: web-service
  replicas: 1
  template:
```
</div>
<div>

**Namespaces** organize resources in the the cluster
- See just those components relevant to a project
- Avoid name collisions across projects
- Restrict access with RBAC
- Limit resources per project

</div>
</div>

---

## Investigating Namespaces

Show all namespaces:
```bash
kubectl get namespaces
```
Get pods within _my-namespace_
```bash
kubectl get pods -n my-namespace
```
Get pods in all namespaces:
```bash
kubectl get pods --all-namespaces
```

---

## Activity: Investigating Namespaces

<!-- _class: invert -->

1. What namespaces are currently on the cluster?

2. What pods are running in the _kube-system_ namespace?

---

## Adding a Namespace

<div class="columns">
<div>

```yaml
apiVersion: v1
kind: Namespace
metadata:
  name: dso-project
---
```
</div>
<div>

Add this Namespace definition to the beginning of the `web-service.yaml` file
</div>
</div>

---

## Deploy the Deployment

```bash
kubectl apply -f web-service.yaml
```
See if a pod got created
```bash
kubectl get pods -n dso-project
```
Or, switch the current namespace for `kubectl`:
```bash
kubectl config set-context --current --namespace=dso-project
kubectl get pods
```

---

## Deployment Ensures Pods Exist

Delete the current pod:
```bash
kubectl delete pod web-deployment-7447478ddd-j9fv4  # Name will vary
```

See that a new pod gets created:
```bash
kubectl get pods
```

---

## Services: Abstracted Applications

Pods maybe be moved across nodes, change IP address, and get new names (for deployments).  How can we reliably access an application?

A **Service** provides a stable IP and DNS name, routing all traffic to the pods actually running the application.

---

## Creating a Service

<div class="columns">
<div>

```yaml
---
apiVersion: v1
kind: Service
metadata:
  name: web-server
  namespace: dso-project
spec:
  type: ClusterIP
  selector:
    app: web-service
  ports:
    - name: http
      port: 8000
      targetPort: http
```
</div>
<div>

Add another YAML document to `web-service.yaml`
</div>
</div>

---

## Creating a Service: Routing to the Pods

<div class="columns">
<div>

```yaml {8-9,13}
---
apiVersion: v1
kind: Service
metadata:
  name: web-server
  namespace: dso-project
spec:
  type: ClusterIP
  selector:
    app: web-service
  ports:
    - name: http
      port: 8000
      targetPort: http
```
</div>
<div>

The `selector` indicates which pods should be routed to as part of this service

`targetPort` indicates the port on that pod to receive the traffic
</div>
</div>

---

## Creating a Service

<div class="columns">
<div>

```yaml {8}
---
apiVersion: v1
kind: Service
metadata:
  name: web-server
  namespace: dso-project
spec:
  type: ClusterIP
  selector:
    app: web-service
  ports:
    - name: http
      port: 8000
      targetPort: http
```
</div>
<div>

- **ClusterIP:** Service accessible only inside cluster (the default)
- **NodePort:** Opens a port on _every_ node in the cluster
  - All traffic to that port routes to service
- **LoadBalancer:** Provisions a load balancer routing service
  - Requires provider support
</div>
</div>

---

## Deploy the Service

```bash
kubectl apply -f web-service.yaml
```
See the service:
```bash
kubectl get service  # or svc
```
Forward a local port to the service:
```bash
kubectl port-forward service/web-server http
```

---

## Activity: Changing the Number of Replicas

<!-- _class: invert -->

1. Increase the number of replicas in the deployment YAML

2. Deploy the updated YAML

3. Check that the expected number of pods have been created

4. Try accessing the service through port-forwarding

---

## Serving with a LoadBalancer

`kubectl port-forward` always routes to the same pod for a service
<!-- That's why the count increases steadily -->

Minikube can simulate a LoadBalancer:
1. In a separate terminal, run `minikube tunnel`
2. Change the service's `spec.type` to "LoadBalancer"
3. Re-deploy the service
4. Check the service with `kubectl get svc`
5. User the EXTERNAL-IP of the service to access it:
   `curl http://10.110.165.143:8000/api/visits`

<!--
The visit count should jump around as the load balancer routes you to different services.
-->

---

## Other Ways to Expose Applications

- An **Ingress** routes HTTP(S) traffic to services based on path
  - Allows one load balancer to serve many services
  - Can do SSL/TLS termination
- The **Gateway API** is a new system for managing K8s networking
  - The **Gateway Class** defines the infrastructure
  - The **Gateway** specifies ports, protocols, and TLS termination
  - An **HTTPRoute** maps HTTP traffic to the appropriate service

---

## Activity: Create an Ollama Service

<!-- _class: invert -->

**Ollama** is an inference server: It can run Large Language Models (LLMs) to generate text

In `exercises/ollama-service/ollama-pod.yaml`, there is configuration for a pod that uses Ollama to run the _qwen3:0.6b_ model

Create a Deployment and a Service to run Ollama in the cluster
&rarr; Use the existing _dso-project_ namespace

See `exercises/ollama-service/README.md` for more details

---

## Activity: Create an Ollama Service

A sample solution can be found in `reference/services/ollama.yaml`

Make sure configuration code for the Ollama service is stored in `project/services/`, either from your work or the reference

---

## Access Ollama from Another Pod

Our _web-service_ offers a UI for sending queries to a LLM
$\Rightarrow$ It needs to send queries to the _ollama_ Service

All Services are given names in the cluster DNS.  The service _my-service_ running in _my-namespace_ may be reached at:
- `my-service`, from pods in  _my-namespace_
- `my-service.my-namespace`, from all pods
- `my-service.my-namespace.svc.cluster.local`, for a FQDN

<!--
Pods are also given DNS entries -- replace .svc with .pod
-->

---

## Getting a Debugging Pod

Often useful to create a pod and get shell to debug network issues:
```bash
kubectl run debug-pod -it --rm --image=nicolaka/netshoot --restart=Never -- sh
```
- `debug-pod` is pod name; is arbitrary
- `nicolaka/netshoot` has several network troubleshooting tools
  - Also, `busybox` is very lightweight Linux shell
- `-- sh`: Run the _sh_ shell
  - Alternatively, `bash` is often available

<!--
Check that we can talk to the ollama pod:
curl -w "\n" http://ollama-service:11434
curl -w "\n" http://ollama-service.dso-project:11434
curl -w "\n" http://ollama-service.dso-project.svc.cluster.local:11434
-->

---

## Setting Environmental Variables

<style scoped>
  pre {
    font-size: 0.95em;
  }
</style>

The _web-service_ application uses the `OLLAMA_URL` environmental variable to find the Ollama server

Add to the _web-service_ Deployment:
```yaml {6-9}
spec:
  template:
    spec:
      containers:
        - name: web-service
          env:
            - name: OLLAMA_URL
              value: "http://ollama-service.dso-project.svc.cluster.local:11434"
```

---

## Activity: Test the Web Site

<!-- _class: invert -->

1. Deploy the updated deployment.

2. Set up port-forwarding for the service. (Codespaces doesn't make accessing a minikube tunnel address easy.)

3. Visit the site in your browser, and try asking a question.

---

## Persisting the Visit Counter

- Currently, each pod keeps its own visit count
  - Count gets reset when pod deleted and recreated
  - Count depends on which pod you reach
- Could move to StatefulSet; give each pod a Persistent Volume
  - Would still need a consensus algorithm to merge counts
- Better approach: Separate persistence service
  - **A database**

---

## Adding an Object Store

- Our needs are minimal $\Rightarrow$ Almost any database would work
- We choose to use an S3-compatible object store
  - Store and retrieve files at a given key
  - Plenty of tooling for Amazon's S3 to reuse
  - Our Python server accepts S3 URLs for the counter file
- We have selected [Garage](https://garagehq.deuxfleurs.fr/) as our object store

<!--
Initial plan had been to use MinIO, a leader in this space.
But they just shut down their open-source offering.
Garage is a promising replacement, but not the only option.
-->

---

## Helm Configures a Configuration

- Projects such as Garage require many resources to be configured
- We could write a bunch of YAML documents, but &hellip;
  - Most deploys will look about the same
  - We need to make sure names are consistent across resources
- **Helm** is a package manager for Kubernetes
  - Works from a **chart**, a set of templated configuration files
  - Customized values can be inserted during deployment

---

## Helm Charts

- Helm charts can be:
  - Read from a Helm **repository**
  - A local `.tgz` file with the appropriate structure
  - A local directory with the appropriate structure
- We will use a Helm chart from [datahub-local/garage-helm](https://github.com/datahub-local/garage-helm)

<!--
Poke into the garage directory in the repo.  This is the chart.
- Chart.yaml gives metadata
- templates/ has a bunch of YAML files
  - templates/service.yaml: Looks like a Service config, but with weird templating stuff
- values.yaml holds default values that get templated into the chart
-->

---

## Getting the Chart

Add the repo with this chart to our Helm configuration:
```bash
helm repo add garage-helm https://datahub-local.github.io/garage-helm
```

See all of the configurable values for the `garage-helm/garage` chart:
```bash
helm show values garage-helm/garage
```

---

## Configuring Our Installation

<div class="columns">
<div>

```yaml
deployment:
  replicaCount: 1

garage:
  replicationFactor: "1"

persistence:
  enabled: true
  data:
    storageClass: standard
    size: 1Gi
  meta:
    storageClass: standard
    size: 100Mi
```
</div>
<div>

```yaml
clusterConfig:
  enabled: true
  buckets:
    - name: visitors
  keys:
    my-key:
      keyId: GK012...4567
      secretKey: 0123...abcdef
      buckets:
        - visitors
```

Full file at `reference/services/garage.yaml`

<!--
Got these values mostly from the documentation.  And some trial-and-error.

Note the clusterConfig will create a bucket (top-level structure) named
`visitors` and set a key with access permissions.  We'll use that to store
the visit count.
-->

</div>
</div>

---

## Installing the Chart

Install the chart with our configuration:
```bash
helm install garage garage-helm/garage --namespace garage \
  --create-namespace --values garage.yaml
```
This will take a few minutes to run

Once finished, check for services and pods:
```bash
kubectl get service -n garage
kubectl get pods -n garage
```

---

## Breaking Down the Install Command

```bash
helm install garage \   # This is the name of the installation.  It is used
                        # both in helm itself and within k8s resources.

  garage-helm/garage \  # The name of the helm chart in the helm repo.

  --namespace garage \  # The k8s namespace where we will deploy this.

  --create-namespace \  # Create that namespace during installation.

  --values garage.yaml  # Load values from this file.
```

---

## Activity: Make _web-service_ Use Garage

<!-- _class: invert -->

The _web-service_ can be configured to use Garage by setting these environmental variables in the Pods:

`AWS_ENDPOINT_URL`: _http:&zwnj;//garage.garage.svc.cluster.local:3900_
`AWS_ACCESS_KEY_ID`: The `keyId` in the Garage configuration file
`AWS_SECRET_ACCESS_KEY`: The `secretKey` in the Garage configuration
`VISIT_COUNTER_FILE`: _s3://visitors/visit.txt_

Deploy the updated service.  Now the visit counter should persist even when the underlying pods are restarted.

---

## Other Kubernetes Topics

<!-- _class: lead -->

<!--
Things worth knowing about, that I don't have time for right now.
Some of these we will see in the coming weeks
-->

---

## Kubenetes Dashboard

The currently-recommended dashboard is [Headlamp](https://headlamp.dev/), which can run as an local desktop application, or on the cluster itself
<small>I'd recommend running locally for production</small>

```bash
# Minikube-specific instructions
minikube addons enable headlamp
minikube addons enable metrics-server

kubectl create token headlamp -n headlamp  # Copy this value

kubectl port-forward -n headlamp service/headlamp 8080:80 --address 0.0.0.0
```
Use token to authenticate with UI

---

## Network Policies

By default, all pods can communicate with each other

Adding a **NetworkPolicy** switches this to _default-deny_
&rarr; Only explicitly allowed traffic is permitted

Rules based on pod labels, namespace labels, or IP blocks

_E.g._ The _web-service_ should only have
- Incoming traffic on port 8000
- Outgoing traffic to DNS and _ollama_

---

## Resource Requests and Limits

- Resource **requests** and **limits** govern how much CPU and memory a pod may consume
  - CPU measured in _cores_ or _millicores_ (`250m` = ¼ core)
  - Memory in bytes, usually with suffixes (`Mi` = $2^{20}$, `Gi` = $2^{30}$)
- Requests are used when scheduling pods on nodes
  - The total requested by all pods cannot exceed total available
- Limits enforced at runtime
  - CPU usage throttled
  - Excess memory usage results in OOM kill

---

## Role-Based Access Control (RBAC)

- **Roles** describe certain capabilities: what actions are allows on which resources
- **RoleBindings** grant certain roles to certain **Users**
- Users may be:
  - Human users, managed outside of Kubernetes
  - Service Accounts, allowing pods to communicate with the K8s API server

---

## Matching Pods to Nodes

The **kube-scheduler** decides which node hosts which pods

Modern AI workloads need certain pods running on specific hardware

- A **node selector** on a pod specifies labels that must be present on the node to which it is assigned
- A **node affinity** on a pod expresses a preference about where the pod should be scheduled
- A **taint** on a node prevents pods from being scheduled there if they don't have a matching **toleration**

---

## Container Probes

- **Probes** are used to check on container status
  - **startupProbe** checks if a container has finished starting
    - Other probes disabled until it succeeds
    - Stops checking after success
  - **readinessProbe** checks if container is ready for traffic
    - Services only send traffic to ready containers
  - **livenessProbe** checks if container is still working
    - Container will be killed and restarted on failure

<!--
Readiness can depend on the whole system; liveness should depend only on
the container itself.  If a web-server can't reach the database, it can
report not-ready, as it can't serve traffic.  But it shouldn't report
not-live, else it will be killed.  If there's a problem with the DB, we'll
end up with a loop where we keep killing all the web server containers,
they keep trying to reconnect to the DB, and thus they keep the DB from
starting up correctly.
-->

---

## Feedback

<!-- _class: lead invert -->
![](images/session3-qr.png)

[form.typeform.com/to/RkXh2Poj](https://form.typeform.com/to/RkXh2Poj)

<!--
Form link: https://form.typeform.com/to/RkXh2Poj
-->
