<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Energy Consumption Anomaly Detection & GRU Forecasting</title>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/tensorflow/4.10.0/tf.min.js"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/Chart.js/3.9.1/chart.min.js"></script>
    <style>
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            margin: 0;
            padding: 20px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: #333;
            min-height: 100vh;
        }
        .container {
            max-width: 1400px;
            margin: 0 auto;
            background: rgba(255, 255, 255, 0.95);
            border-radius: 20px;
            padding: 30px;
            box-shadow: 0 20px 60px rgba(0, 0, 0, 0.1);
            backdrop-filter: blur(10px);
        }
        h1 {
            text-align: center;
            color: #2c3e50;
            margin-bottom: 30px;
            font-size: 2.5em;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.1);
        }
        .controls {
            display: flex;
            gap: 15px;
            margin-bottom: 30px;
            flex-wrap: wrap;
            justify-content: center;
        }
        button {
            background: linear-gradient(145deg, #3498db, #2980b9);
            color: white;
            border: none;
            padding: 12px 24px;
            border-radius: 25px;
            cursor: pointer;
            font-size: 14px;
            font-weight: 600;
            transition: all 0.3s ease;
            box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2);
        }
        button:hover {
            transform: translateY(-2px);
            box-shadow: 0 6px 20px rgba(0, 0, 0, 0.3);
        }
        button:disabled {
            background: #95a5a6;
            cursor: not-allowed;
            transform: none;
        }
        .charts-container {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(600px, 1fr));
            gap: 30px;
            margin-bottom: 30px;
        }
        .chart-wrapper {
            background: white;
            border-radius: 15px;
            padding: 20px;
            box-shadow: 0 8px 25px rgba(0, 0, 0, 0.1);
            border: 1px solid #e0e6ed;
        }
        .chart-title {
            font-size: 1.3em;
            font-weight: 600;
            margin-bottom: 15px;
            color: #2c3e50;
            text-align: center;
        }
        .stats {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }
        .stat-card {
            background: linear-gradient(145deg, #ffffff, #f8f9fa);
            border-radius: 15px;
            padding: 20px;
            text-align: center;
            box-shadow: 0 8px 25px rgba(0, 0, 0, 0.1);
            border: 1px solid #e0e6ed;
        }
        .stat-number {
            font-size: 2em;
            font-weight: bold;
            color: #3498db;
            margin-bottom: 5px;
        }
        .stat-label {
            color: #7f8c8d;
            font-size: 0.9em;
            font-weight: 500;
        }
        .progress-bar {
            width: 100%;
            height: 8px;
            background: #ecf0f1;
            border-radius: 4px;
            overflow: hidden;
            margin: 20px 0;
        }
        .progress-fill {
            height: 100%;
            background: linear-gradient(90deg, #3498db, #2ecc71);
            border-radius: 4px;
            transition: width 0.3s ease;
        }
        .log {
            background: #2c3e50;
            color: #ecf0f1;
            padding: 20px;
            border-radius: 15px;
            font-family: 'Monaco', 'Menlo', monospace;
            font-size: 13px;
            height: 200px;
            overflow-y: auto;
            margin-top: 20px;
            box-shadow: inset 0 4px 8px rgba(0, 0, 0, 0.3);
        }
        #anomalyThreshold {
            width: 100px;
            padding: 8px;
            border-radius: 8px;
            border: 2px solid #ddd;
            font-size: 14px;
        }
        .threshold-container {
            display: flex;
            align-items: center;
            gap: 10px;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🔋 Energy Consumption Anomaly Detection & GRU Forecasting</h1>
        
        <div class="controls">
            <button onclick="generateData()">Generate Data</button>
            <button onclick="detectAnomalies()" id="detectBtn" disabled>Detect Anomalies</button>
            <button onclick="removeAnomalies()" id="removeBtn" disabled>Remove Anomalies</button>
            <button onclick="trainModel()" id="trainBtn" disabled>Train GRU Model</button>
            <button onclick="makePredictions()" id="predictBtn" disabled>Make Predictions</button>
            <div class="threshold-container">
                <label>Threshold:</label>
                <input type="number" id="anomalyThreshold" value="2.5" min="1" max="5" step="0.1">
            </div>
        </div>

        <div class="progress-bar">
            <div class="progress-fill" id="progressFill" style="width: 0%"></div>
        </div>

        <div class="stats">
            <div class="stat-card">
                <div class="stat-number" id="dataPoints">0</div>
                <div class="stat-label">Data Points</div>
            </div>
            <div class="stat-card">
                <div class="stat-number" id="anomaliesFound">0</div>
                <div class="stat-label">Anomalies Found</div>
            </div>
            <div class="stat-card">
                <div class="stat-number" id="cleanData">0</div>
                <div class="stat-label">Clean Data Points</div>
            </div>
            <div class="stat-card">
                <div class="stat-number" id="modelAccuracy">0%</div>
                <div class="stat-label">Model Accuracy</div>
            </div>
        </div>

        <div class="charts-container">
            <div class="chart-wrapper">
                <div class="chart-title">Original Energy Consumption Data</div>
                <canvas id="originalChart"></canvas>
            </div>
            <div class="chart-wrapper">
                <div class="chart-title">Anomaly Detection Results</div>
                <canvas id="anomalyChart"></canvas>
            </div>
            <div class="chart-wrapper">
                <div class="chart-title">Clean Data & GRU Predictions</div>
                <canvas id="predictionChart"></canvas>
            </div>
            <div class="chart-wrapper">
                <div class="chart-title">Model Training Loss</div>
                <canvas id="lossChart"></canvas>
            </div>
        </div>

        <div class="log" id="logContainer"></div>
    </div>

    <script>
        // Global variables
        let rawData = [];
        let cleanData = [];
        let anomalies = [];
        let model = null;
        let predictions = [];
        let trainingLoss = [];

        // Chart instances
        let originalChart, anomalyChart, predictionChart, lossChart;

        function log(message) {
            const logContainer = document.getElementById('logContainer');
            const timestamp = new Date().toLocaleTimeString();
            logContainer.innerHTML += `[${timestamp}] ${message}\n`;
            logContainer.scrollTop = logContainer.scrollHeight;
        }

        function updateProgress(percent) {
            document.getElementById('progressFill').style.width = percent + '%';
        }

        function updateStats() {
            document.getElementById('dataPoints').textContent = rawData.length;
            document.getElementById('anomaliesFound').textContent = anomalies.length;
            document.getElementById('cleanData').textContent = cleanData.length;
        }

        // Generate synthetic energy consumption data
        function generateData() {
            log("Generating synthetic energy consumption data...");
            updateProgress(20);

            const hours = 24 * 30; // 30 days of hourly data
            rawData = [];
            
            for (let i = 0; i < hours; i++) {
                const hour = i % 24;
                const day = Math.floor(i / 24) % 7;
                
                // Base consumption pattern
                let baseConsumption = 50 + 30 * Math.sin(2 * Math.PI * hour / 24); // Daily pattern
                baseConsumption += 10 * Math.sin(2 * Math.PI * day / 7); // Weekly pattern
                
                // Add noise
                const noise = (Math.random() - 0.5) * 10;
                let consumption = baseConsumption + noise;
                
                // Add some anomalies (5% chance)
                if (Math.random() < 0.05) {
                    consumption += (Math.random() - 0.5) * 100; // Large anomaly
                }
                
                rawData.push({
                    hour: i,
                    consumption: Math.max(0, consumption),
                    timestamp: new Date(Date.now() - (hours - i) * 60 * 60 * 1000)
                });
            }

            updateProgress(100);
            log(`Generated ${rawData.length} data points`);
            updateStats();
            
            // Plot original data
            plotOriginalData();
            
            // Enable next button
            document.getElementById('detectBtn').disabled = false;
        }

        function plotOriginalData() {
            const ctx = document.getElementById('originalChart').getContext('2d');
            if (originalChart) originalChart.destroy();
            
            originalChart = new Chart(ctx, {
                type: 'line',
                data: {
                    labels: rawData.map(d => d.hour),
                    datasets: [{
                        label: 'Energy Consumption (kWh)',
                        data: rawData.map(d => d.consumption),
                        borderColor: '#3498db',
                        backgroundColor: 'rgba(52, 152, 219, 0.1)',
                        fill: true,
                        tension: 0.1,
                        pointRadius: 0
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    scales: {
                        x: { title: { display: true, text: 'Hour' } },
                        y: { title: { display: true, text: 'Consumption (kWh)' } }
                    },
                    plugins: { legend: { display: true } }
                }
            });
        }

        // Anomaly detection using multiple techniques
        async function detectAnomalies() {
            log("Starting anomaly detection...");
            updateProgress(20);

            const threshold = parseFloat(document.getElementById('anomalyThreshold').value);
            anomalies = [];

            // 1. Statistical Z-Score method
            log("Applying Z-Score anomaly detection...");
            const values = rawData.map(d => d.consumption);
            const mean = values.reduce((a, b) => a + b) / values.length;
            const std = Math.sqrt(values.reduce((sq, n) => sq + Math.pow(n - mean, 2), 0) / values.length);
            
            updateProgress(40);

            // 2. Isolation Forest-like approach (simplified)
            log("Applying statistical outlier detection...");
            const q1 = quantile(values, 0.25);
            const q3 = quantile(values, 0.75);
            const iqr = q3 - q1;
            const lowerBound = q1 - 1.5 * iqr;
            const upperBound = q3 + 1.5 * iqr;

            updateProgress(60);

            // 3. Moving average deviation
            log("Applying moving average anomaly detection...");
            const windowSize = 24; // 24 hours
            
            rawData.forEach((point, index) => {
                let isAnomaly = false;
                let reason = '';

                // Z-Score test
                const zScore = Math.abs((point.consumption - mean) / std);
                if (zScore > threshold) {
                    isAnomaly = true;
                    reason += `Z-Score: ${zScore.toFixed(2)} > ${threshold}; `;
                }

                // IQR test
                if (point.consumption < lowerBound || point.consumption > upperBound) {
                    isAnomaly = true;
                    reason += `IQR outlier; `;
                }

                // Moving average test
                if (index >= windowSize) {
                    const windowData = rawData.slice(index - windowSize, index);
                    const windowMean = windowData.reduce((sum, d) => sum + d.consumption, 0) / windowSize;
                    const deviation = Math.abs(point.consumption - windowMean);
                    const windowStd = Math.sqrt(windowData.reduce((sq, d) => sq + Math.pow(d.consumption - windowMean, 2), 0) / windowSize);
                    
                    if (deviation > threshold * windowStd) {
                        isAnomaly = true;
                        reason += `Moving avg deviation; `;
                    }
                }

                if (isAnomaly) {
                    anomalies.push({
                        index: index,
                        hour: point.hour,
                        consumption: point.consumption,
                        reason: reason.trim()
                    });
                }
            });

            updateProgress(100);
            log(`Found ${anomalies.length} anomalies using multiple detection techniques`);
            updateStats();
            
            plotAnomalyResults();
            document.getElementById('removeBtn').disabled = false;
        }

        function quantile(arr, q) {
            const sorted = [...arr].sort((a, b) => a - b);
            const pos = (sorted.length - 1) * q;
            const base = Math.floor(pos);
            const rest = pos - base;
            if (sorted[base + 1] !== undefined) {
                return sorted[base] + rest * (sorted[base + 1] - sorted[base]);
            } else {
                return sorted[base];
            }
        }

        function plotAnomalyResults() {
            const ctx = document.getElementById('anomalyChart').getContext('2d');
            if (anomalyChart) anomalyChart.destroy();
            
            const normalData = rawData.filter((_, i) => !anomalies.some(a => a.index === i));
            const anomalyData = anomalies.map(a => ({ x: a.hour, y: a.consumption }));

            anomalyChart = new Chart(ctx, {
                type: 'scatter',
                data: {
                    datasets: [{
                        label: 'Normal Data',
                        data: normalData.map(d => ({ x: d.hour, y: d.consumption })),
                        borderColor: '#2ecc71',
                        backgroundColor: 'rgba(46, 204, 113, 0.6)',
                        pointRadius: 2
                    }, {
                        label: 'Anomalies',
                        data: anomalyData,
                        borderColor: '#e74c3c',
                        backgroundColor: 'rgba(231, 76, 60, 0.8)',
                        pointRadius: 4
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    scales: {
                        x: { title: { display: true, text: 'Hour' } },
                        y: { title: { display: true, text: 'Consumption (kWh)' } }
                    },
                    plugins: { legend: { display: true } }
                }
            });
        }

        function removeAnomalies() {
            log("Removing detected anomalies...");
            updateProgress(50);

            cleanData = rawData.filter((_, index) => !anomalies.some(a => a.index === index));
            
            updateProgress(100);
            log(`Removed ${anomalies.length} anomalies. Clean dataset has ${cleanData.length} points`);
            updateStats();
            
            document.getElementById('trainBtn').disabled = false;
        }

        // Create 3-layer GRU model
        async function trainModel() {
            log("Building 3-layer GRU model...");
            updateProgress(10);

            // Prepare data for training
            const sequenceLength = 24; // Use 24 hours to predict next hour
            const { xs, ys } = createSequences(cleanData.map(d => d.consumption), sequenceLength);
            
            log(`Created ${xs.length} training sequences`);
            updateProgress(30);

            // Build the model
            model = tf.sequential({
                layers: [
                    // First GRU layer
                    tf.layers.gru({
                        units: 64,
                        returnSequences: true,
                        inputShape: [sequenceLength, 1]
                    }),
                    tf.layers.dropout({ rate: 0.2 }),
                    
                    // Second GRU layer
                    tf.layers.gru({
                        units: 32,
                        returnSequences: true
                    }),
                    tf.layers.dropout({ rate: 0.2 }),
                    
                    // Third GRU layer
                    tf.layers.gru({
                        units: 16,
                        returnSequences: false
                    }),
                    tf.layers.dropout({ rate: 0.1 }),
                    
                    // Dense output layer
                    tf.layers.dense({ units: 1, activation: 'linear' })
                ]
            });

            model.compile({
                optimizer: tf.train.adam(0.001),
                loss: 'meanSquaredError',
                metrics: ['mae']
            });

            log("Model architecture created. Starting training...");
            updateProgress(50);

            // Convert to tensors
            const trainX = tf.tensor3d(xs);
            const trainY = tf.tensor2d(ys);

            trainingLoss = [];
            
            // Train the model
            const history = await model.fit(trainX, trainY, {
                epochs: 50,
                batchSize: 32,
                validationSplit: 0.2,
                callbacks: {
                    onEpochEnd: (epoch, logs) => {
                        trainingLoss.push({ epoch: epoch + 1, loss: logs.loss, valLoss: logs.val_loss });
                        if (epoch % 5 === 0) {
                            log(`Epoch ${epoch + 1}/50 - Loss: ${logs.loss.toFixed(4)}, Val Loss: ${logs.val_loss.toFixed(4)}`);
                        }
                        updateProgress(50 + (epoch + 1) / 50 * 40);
                    }
                }
            });

            // Calculate accuracy (using MAPE)
            const predictions = model.predict(trainX);
            const predArray = await predictions.data();
            const actualArray = await trainY.data();
            
            let mape = 0;
            for (let i = 0; i < predArray.length; i++) {
                mape += Math.abs((actualArray[i] - predArray[i]) / actualArray[i]);
            }
            mape = (1 - mape / predArray.length) * 100;
            
            document.getElementById('modelAccuracy').textContent = Math.max(0, mape).toFixed(1) + '%';

            trainX.dispose();
            trainY.dispose();
            predictions.dispose();

            updateProgress(100);
            log("Model training completed!");
            log(`Final validation loss: ${history.history.val_loss[history.history.val_loss.length - 1].toFixed(4)}`);
            
            plotTrainingLoss();
            document.getElementById('predictBtn').disabled = false;
        }

        function createSequences(data, seqLength) {
            const xs = [], ys = [];
            for (let i = 0; i < data.length - seqLength; i++) {
                xs.push(data.slice(i, i + seqLength).map(x => [x]));
                ys.push([data[i + seqLength]]);
            }
            return { xs, ys };
        }

        function plotTrainingLoss() {
            const ctx = document.getElementById('lossChart').getContext('2d');
            if (lossChart) lossChart.destroy();
            
            lossChart = new Chart(ctx, {
                type: 'line',
                data: {
                    labels: trainingLoss.map(d => d.epoch),
                    datasets: [{
                        label: 'Training Loss',
                        data: trainingLoss.map(d => d.loss),
                        borderColor: '#e74c3c',
                        backgroundColor: 'rgba(231, 76, 60, 0.1)',
                        fill: false
                    }, {
                        label: 'Validation Loss',
                        data: trainingLoss.map(d => d.valLoss),
                        borderColor: '#f39c12',
                        backgroundColor: 'rgba(243, 156, 18, 0.1)',
                        fill: false
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    scales: {
                        x: { title: { display: true, text: 'Epoch' } },
                        y: { title: { display: true, text: 'Loss' } }
                    },
                    plugins: { legend: { display: true } }
                }
            });
        }

        async function makePredictions() {
            log("Making predictions with trained GRU model...");
            updateProgress(30);

            const sequenceLength = 24;
            const lastSequence = cleanData.slice(-sequenceLength).map(d => d.consumption);
            
            predictions = [];
            let currentSequence = [...lastSequence];
            
            // Predict next 48 hours
            for (let i = 0; i < 48; i++) {
                const input = tf.tensor3d([currentSequence.map(x => [x])]);
                const pred = model.predict(input);
                const predValue = await pred.data();
                
                predictions.push({
                    hour: cleanData.length + i,
                    consumption: predValue[0]
                });
                
                // Update sequence for next prediction
                currentSequence.shift();
                currentSequence.push(predValue[0]);
                
                input.dispose();
                pred.dispose();
                
                if (i % 10 === 0) {
                    updateProgress(30 + (i / 48) * 60);
                }
            }

            updateProgress(100);
            log(`Generated ${predictions.length} predictions`);
            
            plotPredictions();
        }

        function plotPredictions() {
            const ctx = document.getElementById('predictionChart').getContext('2d');
            if (predictionChart) predictionChart.destroy();
            
            // Show last 100 points of clean data + predictions
            const recentData = cleanData.slice(-100);
            
            predictionChart = new Chart(ctx, {
                type: 'line',
                data: {
                    labels: [...recentData.map(d => d.hour), ...predictions.map(p => p.hour)],
                    datasets: [{
                        label: 'Clean Historical Data',
                        data: [...recentData.map(d => d.consumption), ...Array(predictions.length).fill(null)],
                        borderColor: '#2ecc71',
                        backgroundColor: 'rgba(46, 204, 113, 0.1)',
                        fill: false,
                        pointRadius: 1
                    }, {
                        label: 'GRU Predictions',
                        data: [...Array(recentData.length).fill(null), ...predictions.map(p => p.consumption)],
                        borderColor: '#9b59b6',
                        backgroundColor: 'rgba(155, 89, 182, 0.1)',
                        fill: false,
                        borderDash: [5, 5],
                        pointRadius: 2
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    scales: {
                        x: { title: { display: true, text: 'Hour' } },
                        y: { title: { display: true, text: 'Consumption (kWh)' } }
                    },
                    plugins: { legend: { display: true } }
                }
            });
        }

        // Initialize
        log("Energy Consumption Anomaly Detection & GRU Forecasting System Initialized");
        log("Click 'Generate Data' to start the process");
    </script>
</body>
</html>