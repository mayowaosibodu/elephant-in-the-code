#!/usr/bin/env bash

# Create directory structure
mkdir -p mock_network/app_server/routes
mkdir -p mock_network/app_server/logs
mkdir -p mock_network/user_directory
mkdir -p mock_network/service_secrets
mkdir -p mock_network/infra

###########################################
# Populate app_server/
###########################################

cat > mock_network/app_server/server_config.json << 'EOF'
{
  "port": 8080,
  "mode": "development",
  "enableMetrics": true,
  "authStrategy": "token"
}
EOF

cat > mock_network/app_server/routes/dashboard.js << 'EOF'
// Route: Dashboard
function getDashboard(req, res) {
    // Render dashboard page
    res.send("Dashboard data");
}
EOF

cat > mock_network/app_server/routes/metrics.js << 'EOF'
// Route: Metrics
function getMetrics(req, res) {
    // Render metrics
    res.send("Metrics data");
}
EOF

cat > mock_network/app_server/routes/logs.js << 'EOF'
// Route: Logs
function getLogs(req, res) {
    // Show logs
    res.send("Logs data");
}
EOF

cat > mock_network/app_server/logs/app.log << 'EOF'
[INFO] App server started successfully.
[INFO] Listening on port 8080.
EOF

cat > mock_network/app_server/logs/metrics.log << 'EOF'
[METRICS] CPU Usage: 23%
[METRICS] Memory Usage: 58%
EOF


###########################################
# Populate user_directory/
###########################################

cat > mock_network/user_directory/users.json << 'EOF'
[
  {"username": "alice", "role": "admin"},
  {"username": "bob", "role": "editor"},
  {"username": "carol", "role": "viewer"}
]
EOF

cat > mock_network/user_directory/permissions.json << 'EOF'
{
  "admin": ["read", "write", "delete", "configure"],
  "editor": ["read", "write"],
  "viewer": ["read"]
}
EOF


###########################################
# Populate service_secrets/
###########################################

cat > mock_network/service_secrets/credentials_sample.txt << 'EOF'
# These are NOT real credentials.
# Placeholder values for safe demo purposes only.

USER_TOKEN=PLACEHOLDER_TOKEN_123
SERVICE_KEY=DEMO_ONLY_NOT_REAL
EOF

cat > mock_network/service_secrets/tokens_example.txt << 'EOF'
# Mock tokens (non-sensitive, for demonstration only)

TEMP_TOKEN=ABC123_FAKE
SESSION_ID=XYZ789_FAKE
EOF


###########################################
# Populate infra/
###########################################

cat > mock_network/infra/topology.json << 'EOF'
{
  "services": ["app_server", "auth_proxy", "metrics"],
  "connections": {
    "app_server": ["auth_proxy"],
    "auth_proxy": ["metrics"]
  }
}
EOF

cat > mock_network/infra/deployment_notes.txt << 'EOF'
Deployment Notes (Demo Only)

- Ensure service dependencies are configured.
- Update topology if new microservices are added.
EOF

echo "Mock network environment created successfully."
