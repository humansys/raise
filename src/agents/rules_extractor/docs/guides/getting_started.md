# Getting Started with Rules Extractor

This guide will help you get started with using the Rules Extractor component to analyze legacy code and extract business rules.

## Prerequisites

- Python 3.8 or higher
- Virtual environment tool (venv)
- OpenRouter API key

## Installation

1. Clone the repository:
```bash
git clone https://github.com/your-org/raise-mcp.git
cd raise-mcp
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up environment variables:
```bash
cp .env.example .env
# Edit .env and add your OpenRouter API key
```

## Basic Usage

### Command Line Interface

The simplest way to use the Rules Extractor is through the provided shell script:

```bash
# Process a specific file
./run_extractor.sh path/to/your/code.rpgle

# Run with default test cases
./run_extractor.sh
```

### Python API

You can also use the Rules Extractor in your Python code:

```python
from rules_extractor.extractor import RuleExtractor

# Initialize the extractor
extractor = RuleExtractor()

# Read your code file
with open('path/to/your/code.rpgle', 'r') as f:
    code = f.read()

# Extract rules
rules = extractor.extract_rules(code)

# Process the results
for rule in rules:
    print(f"Found rule: {rule.id}")
    print(f"Description: {rule.description}")
    print(f"Confidence: {rule.confidence}")
    print("---")
```

## Configuration

### Environment Variables

- `OPENROUTER_API_KEY`: Your OpenRouter API key
- `LOG_LEVEL`: Logging level (DEBUG, INFO, WARNING, ERROR)
- `DEBUG_LLM_RESPONSE`: Set to "True" to see raw LLM responses

### Logging

The component uses Python's logging module. To enable debug logging:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## Example Files

The `examples` directory contains sample code files you can use to test the extractor:

```bash
# Process an example file
./run_extractor.sh examples/sample_rpgle.txt
```

## Troubleshooting

### Common Issues

1. **API Key Not Found**
   ```
   ValueError: API key is missing. Set the OPENROUTER_API_KEY environment variable.
   ```
   Solution: Make sure you've set up your `.env` file with a valid API key.

2. **File Encoding Issues**
   ```
   UnicodeDecodeError: 'utf-8' codec can't decode byte...
   ```
   Solution: Ensure your input files are properly encoded (UTF-8 recommended).

3. **No Rules Found**
   - Check if your code contains business logic
   - Try increasing the chunk size
   - Enable debug logging to see the LLM responses

### Getting Help

- Check the API documentation in `docs/api/`
- Review the example files
- Submit issues on GitHub

## Next Steps

- Learn about the [BusinessRule model](../api/README.md#businessrule)
- Explore [advanced configuration options](../api/README.md#configuration)
- Contribute to the project 