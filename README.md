# Power Broker AI Summaries

Read the summaries: https://sandr.in/power-broker/

This is a project to create AI generated summaries of each chapter of the book
"The Power Broker" by Robert Caro.

# Running

Copy the example config:

```bash
cp src/config.example.py src/config.py
```

Add you OpenAI API key to `config.py`:

```python
OPENAI_API_KEY="xxx"
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Run:

```
make summary
```
