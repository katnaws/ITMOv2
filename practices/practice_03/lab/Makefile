.PHONY: install test build-models build-experiment build-agent qa compare
install:
	@python3 -c "import sys; assert sys.version_info >= (3,10), 'Python 3.10+ required'; print('Standard library only: ready')"
test: install
	$(MAKE) -C demo test

# Build local Ollama models from Modelfiles
build-models: build-experiment build-agent

# itmo-experiment: 4k model with a grounded, non-thinking system prompt.
# The baseline/system comparison in experiment.py intentionally uses qwen3.5:4b.
build-experiment:
	@ollama create itmo-experiment -f Modelfile

# itmo-agent: large-context variant for OpenCode agent
build-agent:
	@ollama create itmo-agent -f Modelfile.agent

# Ask five questions to the local model in isolated read-only runs
qa:
	@python3 qa.py

# Compare model answers with golden references
compare:
	@python3 check_answers.py
