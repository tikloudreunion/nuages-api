# Nuages API

## Overview

Nuages API is a RESTful API that allows you to interact with the Nuages platform. It provides endpoints for managing resources, retrieving data, and performing various operations on LXC containers.

## Development

### Requirements

- Python 3.8 or higher
- pip
- virtualenv (optional but recommended)

### Installation

1. Clone the repository:

   ```bash
   git clone git@github.com:tikloudreunion/nuages-api.git
    cd nuages-api
    ```

2. Create a virtual environment (optional but recommended):

    ```bash
    python -m venv .venv
    source .venv/bin/activate
    ```

3. Install the required packages:

    ```bash
    pip install -r requirements.txt
    ```

### Development Server

To run the development server, use the following command:

```bash
fastapi dev --reload nuages-api
```
