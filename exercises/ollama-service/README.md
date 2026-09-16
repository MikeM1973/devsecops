# _ollama-service_ Exercise

[_Ollama_](https://ollama.com/) is an **inference server** for large language models (LLMs).  We will use it to serve the [_qwen3:0.6b_](https://ollama.com/library/qwen3:0.6b) model.

The `ollama-pod.yaml` file gives the configuration to run Ollama as a pod, serving the _qwen3:0.6b_ model.  There are a couple components in this file that you haven't seen yet, but you can probably guess what they do.  It should run as written, although it can take a few minutes to pull the container image the first time.

The pod will run a HTTP server on port 11434.  You may find the following paths interesting:
- `/`: Brief status message
- `/api/tags`: JSON document showing available models
- `/api/generate`: Generate a response to a prompt.  Usage example:
  ```bash
  curl http://localhost:11434/api/generate -d '{
    "model": "qwen3:0.6b",
    "prompt": "What is 2+2?",
    "stream": false
  }'
  ```
  This will run a bit slowly.  The return value includes not only the response, but the thinking trace and other metadata.

## Task

Create a Deployment and a Service to run this pod in the cluster.  You can use the existing _dso-project_ namespace.

We'll be using this service in the project going forward, so it's probably worth placing the configuration files in `project/services/`.
