# Online Proctoring Portal Project

This project consists of three main components: the backend, the portal, and the prediction service. This README provides instructions on how to set up and run each component.

## Project Structure

- **Backend**: Node.js server handling API requests.
- **Portal**: Frontend application built with React.
- **Prediction Service**: Python service for log analysis and prediction.

## Requirements

### Backend

- Node.js (v14 or higher)
- npm (v6 or higher)

### Portal

- Node.js (v14 or higher)
- npm (v6 or higher)

### Prediction Service

- Python 3.6 or higher
- Required Python packages:
  - `numpy`
  - `pandas`
  - `matplotlib`
  - `seaborn`
  - `tqdm` (optional, for progress bar)
  - `xgboost`
  - `scikit-learn`
  - `joblib`

## Installation

### Installing Node.js and npm

#### Windows

1. **Download Node.js**:
   - Visit [nodejs.org](https://nodejs.org/) and download the LTS version for Windows.

2. **Install Node.js**:
   - Run the downloaded installer and follow the prompts to install Node.js and npm.

#### Linux

1. **Install Node.js and npm**:
   ```bash
   sudo apt update
   sudo apt install nodejs npm
   ```

2. **Verify installation**:
   ```bash
   node -v
   npm -v
   ```

### Installing React

1. **Install Create React App**:
   - Open a terminal (Linux) or Command Prompt (Windows) and run:
     ```bash
     npm install -g create-react-app
     ```

2. **Create a new React app**:
   ```bash
   npx create-react-app my-app
   cd my-app
   npm start
   ```

### Installing Python

#### Windows

1. **Download Python**:
   - Visit [python.org](https://www.python.org/downloads/) and download the latest Python installer for Windows.

2. **Install Python**:
   - Run the installer and ensure the option "Add Python to PATH" is checked.

3. **Verify installation**:
   - Open Command Prompt and run:
     ```cmd
     python --version
     ```

#### Linux

1. **Install Python**:
   ```bash
   sudo apt update
   sudo apt install python3 python3-pip
   ```

2. **Verify installation**:
   ```bash
   python3 --version
   ```

## Installation

### Backend

1. **Navigate to the backend directory**:
   ```bash
   cd /path/to/your/project/backend
   ```

2. **Install dependencies**:
   ```bash
   npm install
   ```

3. **Set up environment variables**:
   - Create a `.env` file in the `backend` directory and add necessary environment variables.

4. **Start the server**:
   ```bash
   npm start
   ```

### Portal

1. **Navigate to the portal directory**:
   ```bash
   cd /path/to/your/project/portal
   ```

2. **Install dependencies**:
   ```bash
   npm install
   ```

3. **Start the development server**:
   ```bash
   npm start
   ```

### Prediction Service

1. **Navigate to the prediction service directory**:
   ```bash
   cd /path/to/your/project/prediction_service
   ```

2. **Install required Python packages**:
   ```bash
   pip install numpy pandas matplotlib seaborn tqdm xgboost scikit-learn joblib
   ```

3. **Run the prediction service**:
   ```bash
   python prediction_service.py
   ```

## Running the Project

1. **Start the backend server**:
   - Ensure the backend server is running as described above.

2. **Start the portal**:
   - Ensure the portal is running as described above.

3. **Run the prediction service**:
   - Ensure the prediction service is running as described above.

## Additional Information

- **Backend**: Handles API requests and interacts with the database.
- **Portal**: Provides a user interface for interacting with the backend.
- **Prediction Service**: Analyzes logs and provides predictions based on the data.

## Troubleshooting

- If you encounter any issues, check the console output for error messages.
- Ensure all dependencies are installed and environment variables are set correctly.

Happy coding! 