# FastAPI Project with MongoDB, Vector DB, Redis, and RabbitMQ

This project is a FastAPI application with a MongoDB database, a vector database (such as Qdrant or Milvus), Redis, and RabbitMQ, all managed using Docker Compose. The project uses Poetry for dependency management and includes a convenient bash script for managing Docker services.

## Table of Contents

- [Installation](#installation)
  - [Installing Poetry](#installing-poetry)
    - [macOS](#macos)
    - [Windows](#windows)
    - [Ubuntu](#ubuntu)
- [Setting Up the Project](#setting-up-the-project)
- [Using the Bash Script](#using-the-bash-script)
- [Docker Compose Commands](#docker-compose-commands)

## Installation

### Installing Poetry

Poetry is a dependency manager for Python that helps you manage your project dependencies easily.

#### macOS

To install Poetry on macOS, open your terminal and run the following command:

```bash
curl -sSL https://install.python-poetry.org | python3 -
```

After installation, you might need to add Poetry to your `PATH`. Add the following line to your shell configuration file (`~/.zshrc` or `~/.bash_profile`):

```bash
export PATH="$HOME/.local/bin:$PATH"
```

Then, apply the changes:

```bash
source ~/.zshrc  # or source ~/.bash_profile
```

#### Windows

To install Poetry on Windows, open PowerShell as an administrator and run:

```powershell
(Invoke-WebRequest -Uri https://install.python-poetry.org -UseBasicParsing).Content | python -
```

Ensure that the Python Scripts directory is in your `PATH`. You can check this by running:

```powershell
$env:Path += ";$env:LOCALAPPDATA\Programs\Python\Python39\Scripts"
```

Replace `Python39` with your specific Python version if needed.

#### Ubuntu

To install Poetry on Ubuntu, run the following command:

```bash
curl -sSL https://install.python-poetry.org | python3 -
```

After installing, add Poetry to your `PATH`:

```bash
export PATH="$HOME/.local/bin:$PATH"
```

Add this line to your `.bashrc` or `.zshrc` file to ensure it persists across sessions:

```bash
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc
source ~/.bashrc
```

### Verifying Poetry Installation

To verify that Poetry has been installed correctly, run:

```bash
poetry --version
```

## Setting Up the Project

1. **Clone the repository**:

   ```bash
   git clone https://github.com/hafidabid/fastapi_scaffold_mongodb
   cd fastapi_scaffold_mongodb
   ```

2. **Install dependencies** using Poetry:

   ```bash
   poetry install
   ```

3. **Run the application** using Docker Compose:

   ```bash
   docker compose up -d --build
   ```

## Using the Bash Script

A bash script (`rprod.sh`) is included to help manage your Docker services. This script accepts different arguments to start specific services.

### How to Use the Script

1. **Make the script executable**:

   ```bash
   chmod +x rprod.sh
   ```

2. **Run the script with one of the following arguments**:

   - `service`: Start only the FastAPI service.
   - `service+mongo`: Start the FastAPI service and MongoDB.
   - `service+mongo+redis`: Start the FastAPI service, MongoDB, and Redis.
   - `all`: Start all services (FastAPI, MongoDB, Redis, RabbitMQ, and Vector DB).

   Example usage:

   ```bash
   ./manage_services.sh service+mongo
   ```

## Docker Compose Commands

You can also manually manage services using Docker Compose commands:

- **Start all services**:

  ```bash
  docker compose up -d --build
  ```

- **Stop all services**:

  ```bash
  docker compose down
  ```

- **Start specific services** (e.g., `fastapi_app` and `mongodb`):

  ```bash
  docker compose up -d fastapi_app mongodb
  ```

## Contributing

Feel free to open issues or create pull requests if you find bugs or want to contribute to this project.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
