# LLM Experiments

This repository contains several experiments that attempt to apply Large Language Models to help software development teams with their development processes.

## Installing dependencies

Create a virtual environment, activate it, and install the dependencies:

```console
python -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt
```

## Tests

To run the unit tests:

```console
python -m unittest discover
```

## Experiment 1: summarizing a code base

To summarize a code base, run:

```console
python summarize_code.py <folder>
```
