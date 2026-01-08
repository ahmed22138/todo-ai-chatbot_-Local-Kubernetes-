const express = require('express');
const cors = require('cors');
const mongoose = require('mongoose');
require('dotenv').config();

const app = express();
const PORT = process.env.PORT || 5000;
const MONGODB_URI = process.env.MONGODB_URI || 'mongodb://localhost:27017/todoai';

// Middleware
app.use(cors());
app.use(express.json());

// Health check endpoints
app.get('/health', (req, res) => {
  res.status(200).json({ status: 'healthy', service: 'todo-backend' });
});

app.get('/ready', (req, res) => {
  if (mongoose.connection.readyState === 1) {
    res.status(200).json({ status: 'ready', database: 'connected' });
  } else {
    res.status(503).json({ status: 'not ready', database: 'disconnected' });
  }
});

// Sample todos endpoint
app.get('/api/todos', async (req, res) => {
  res.json([
    { id: 1, title: 'Deploy to Kubernetes', completed: false },
    { id: 2, title: 'Set up Helm charts', completed: false },
    { id: 3, title: 'Validate deployment', completed: false }
  ]);
});

// MongoDB connection
mongoose.connect(MONGODB_URI, {
  useNewUrlParser: true,
  useUnifiedTopology: true
}).then(() => {
  console.log('Connected to MongoDB');
}).catch((err) => {
  console.error('MongoDB connection error:', err);
});

app.listen(PORT, () => {
  console.log(`Backend server running on port ${PORT}`);
});
