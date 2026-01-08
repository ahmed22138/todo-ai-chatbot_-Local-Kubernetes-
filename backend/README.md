## Running the Project with Docker

This project is containerized using Docker and can be run easily with Docker Compose. Below are the project-specific instructions and requirements:

### Requirements
- **Node.js Version:** The Dockerfile uses `node:22.13.1-slim` (set via the `NODE_VERSION` build argument).
- **Dependencies:** Only production dependencies from `package.json` are installed.

### Environment Variables
- The project references a `.env.example` file. If your application requires environment variables, create a `.env` file based on `.env.example` and uncomment the `env_file` line in `docker-compose.yml`.

### Build and Run Instructions
1. **(Optional)** Copy `.env.example` to `.env` and fill in any required values.
2. Build and start the service:
   ```sh
   docker compose up --build
   ```
   This will build the image and start the `javascript-app` service.

### Configuration Notes
- The application runs as a non-root user for improved security.
- No external services or persistent volumes are required.

### Exposed Ports
- The service exposes port **5000** (mapped to host port 5000).

---

**Summary:**
- Build and run with `docker compose up --build`
- Exposed port: 5000
- Set up a `.env` file if your app requires environment variables
