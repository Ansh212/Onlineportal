# Test Data Generator

This folder contains scripts to generate test data for the online portal database. The scripts create realistic user data and test logs with both normal and suspicious behavior patterns.

## Setup

1. Make sure MongoDB is running locally on the default port (27017)
2. Install dependencies:
```bash
npm install
```

## Available Scripts

1. Generate Users:
```bash
npm run generate:users
```
This will create:
- 1 admin user (username: admin, password: admin123)
- 50 regular users with random test registrations and completions

2. Generate Logs:
```bash
npm run generate:logs
```
This will create test logs for all users with:
- Normal behavior patterns (70% of cases)
  - Reasonable time spent on questions (1-5 minutes)
  - Normal page scrolling
  - Few or no tab switches
  
- Suspicious behavior patterns (30% of cases)
  - Very quick responses (10-30 seconds per question)
  - Frequent tab switching
  - Rapid mouse movements
  - Unusual patterns of activity

3. Generate Everything:
```bash
npm run generate:all
```
This will run both scripts in sequence.

## Generated Data Characteristics

### Users
- Distributed across different states and cities
- Random number of registered tests (1-5)
- Random test completion rate (70% chance of completing each registered test)
- Random test scores

### Logs
- Realistic timestamps and activity sequences
- Question-wise time tracking
- Tab switch counting
- Various activity types:
  - Question views
  - Page scrolls
  - Answer submissions
  - Tab switches
  - Mouse movements

## Note
This is for testing purposes only. In production, ensure proper password hashing and security measures are implemented. 