require('dotenv').config();
const express = require('express');
const path = require('path');
const fs = require('fs');
const assessmentsRouter = require('./assessments2');
const scheduler = require('./scheduler');

// Start daily scheduler
try {
  scheduler.startScheduler();
} catch (e) {
  console.error('Failed to start scheduler', e);
}

const app = express();
const PORT = process.env.PORT || 4000;

// Ensure uploads folder exists
const uploadsDir = path.join(__dirname, 'uploads');
if (!fs.existsSync(uploadsDir)) fs.mkdirSync(uploadsDir, { recursive: true });

app.use(express.json());
app.use('/uploads', express.static(uploadsDir));
app.use(express.static(path.join(__dirname, 'public')));
app.use('/api/assessments', assessmentsRouter);
app.use('/api/users', require('./users'));
app.use('/api/dashboard', require('./dashboard'));
app.use('/api/review', require('./review'));

app.get('/health', (req, res) => res.json({ status: 'ok' }));

app.listen(PORT, () => {
  console.log(`Voice assessments backend listening on port ${PORT}`);
});
