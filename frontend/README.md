## Running the Project with Docker

This project is set up to run a React application using Docker and Docker Compose. Below are the specific instructions and requirements for this setup:

### Project-Specific Docker Requirements
- **Node.js Version:** Uses Node.js `22.13.1-slim` (set via the `NODE_VERSION` build argument in the Dockerfile).
- **Static File Server:** The production container installs the `serve` package globally to serve the built React app.
- **Non-root User:** The container runs as a non-root user for improved security.

### Environment Variables
- `NODE_ENV=production` (set in the Dockerfile)
- `PORT=3000` (set in the Dockerfile)
- No additional environment variables are required by default. If you need to add custom environment variables, you can uncomment the `env_file` line in `docker-compose.yml` and provide a `.env` file.

### Build and Run Instructions
1. **Build and Start the App:**
   ```sh
   docker compose up --build
   ```
   This will build the Docker image and start the container for the React app.

2. **Access the App:**
   - The app will be available at [http://localhost:3000](http://localhost:3000)

### Ports
- **Service:** `javascript-app`
- **Exposed Port:** `3000` (mapped to host port 3000)

### Special Configuration
- No volumes or external dependencies are required for this static build.
- The build process uses `npm ci` for installing dependencies (no lock file present).
- The app is served from the `/app/build` directory using the `serve` package.

---
*For any custom environment variables, create a `.env` file and uncomment the `env_file` line in `docker-compose.yml`.*