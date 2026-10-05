.PHONY: install test build-models build-experiment build-agent
install:
	@python3 -c "import sys; assert sys.version_info >= (3,10), 'Python 3.10+ required'; print('Standard library only: ready')"
test: install
	$(MAKE) -C demo test

# Build local Ollama models from Modelfiles
build-models: build-experiment build-agent

# itmo-experiment: smaller context, controlled system prompt
build-experiment:
	@ollama create itmo-experiment -f Modelfile

# itmo-agent: large-context variant for OpenCode agent
build-agent:
	@ollama create itmo-agent -f Modelfile.agent
