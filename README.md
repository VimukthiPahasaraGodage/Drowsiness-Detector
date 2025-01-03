# Drowsiness Detector Chrome Extension

This Chrome extension monitors user drowsiness by analyzing video feed and provides real-time alerts to prevent accidents caused by fatigue.

## Features

- **Real-Time Drowsiness Detection**: Analyzes facial cues to assess user alertness.
- **Immediate Alerts**: Notifies users upon detecting signs of drowsiness.
- **Seamless Integration**: Operates within the Chrome browser without disrupting user experience.

## How It Works

1. **Video Capture**: The extension accesses the user's webcam to capture live video feed.
2. **Data Processing**:
   - The video is segmented and transmitted to AWS API Gateway.
   - AWS Lambda functions process the data and store it in DynamoDB.
   - An EC2 instance analyzes the data to detect drowsiness indicators and logs alerts in DynamoDB.
3. **User Notification**: The extension regularly checks for alerts in DynamoDB and notifies the user if drowsiness is detected.

## Installation

1. **Clone the Repository**:
   ```bash
   git clone https://github.com/VimukthiPahasaraGodage/Drowsiness-Detector.git
