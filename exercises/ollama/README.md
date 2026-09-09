# _ollama_ Exercise

_ollama_ is an **inference server** for large language models (LLMs).  We will use it to serve the _qwen3:0.6b_ model.  It is packaged in the `ollama/ollama` image on [Docker Hub](https://hub.docker.com/r/ollama/ollama).

Once a container is running, the model needs to be download.  Execute within the running container:
```bash
ollama pull qwen3:0.6b
```

The inference server runs on port 11434 within the container.  If that is exposed to localhost, you can get a response from the model with the following command:
```bash
curl http://localhost:11434/api/generate -d '{
  "model": "qwen3:0.6b",
  "prompt": "What is 2+2?",
  "stream": false
}'
```
Replace `prompt` with your query.

Note that the model will be a bit slow.  The return value includes not only the response, but the thinking trace and other metadata.
