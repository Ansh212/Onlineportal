const express = require("express");
const dotenv = require("dotenv");
const cors = require("cors");
const connectDB = require("./config/db");
const authRoutes = require('./routes/auth.routes');
const userRoutes = require('./routes/user.routes');
const testRoutes = require('./routes/test.routes');
const enrollmentRoutes = require('./routes/enrollment.routes');
const take_testRoutes = require('./routes/take_test.routes');
const logRoutes = require('./routes/submit.routes');
const avgTimeRoutes = require('./routes/avgTime.routes');
const avgScoreRoutes = require('./routes/avgScore.routes');
const studentRoutes = require('./routes/studentLogs.routes');
const evaluateTest = require('./routes/flaggedResult.route');
dotenv.config();  

const app = express();

app.use(express.json()); 
app.use(cors());  

connectDB();

// Routes
app.use('/api/auth', authRoutes);
app.use('/api/add', userRoutes);
app.use('/api/get_tests', testRoutes);
app.use('/api/enroll', enrollmentRoutes);
app.use('/api/take_test', take_testRoutes);
app.use('/api/submitTest', logRoutes);
app.use('/api/getAvgTime', avgTimeRoutes);
app.use('/api/avgScore', avgScoreRoutes);
app.use('/api/studentLog', studentRoutes);
app.use('/api/evaluate', evaluateTest);
const PORT = process.env.PORT || 5000;
app.listen(PORT, () => {
  console.log(`Server running on port ${PORT}`);
});
