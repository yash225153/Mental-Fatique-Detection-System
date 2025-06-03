# Mental Fatigue Detector

A comprehensive web application that analyzes mental fatigue using multiple data modalities including typing patterns, mouse movements, and facial analysis, powered by machine learning models.

## 🚀 Features

### Core Functionality
- **Multi-Modal Data Collection**: Captures typing patterns, mouse movements, and facial expressions
- **Real-Time Analysis**: Provides immediate feedback during data collection
- **ML-Powered Insights**: Uses machine learning models for accurate fatigue prediction
- **Dynamic Dashboard**: Displays personalized insights and recommendations
- **Progressive Web App**: Step-by-step data collection process

### Data Collection Modules

#### 1. Typing Pattern Analysis
- **Typing Speed**: Words per minute (WPM) calculation
- **Error Rate**: Backspace usage and correction patterns
- **Pause Frequency**: Typing rhythm and hesitation analysis
- **Real-time Metrics**: Live updates during typing test

#### 2. Mouse Movement Analysis
- **Reaction Time**: Response time to visual targets
- **Movement Accuracy**: Precision of mouse movements
- **Click Patterns**: Mouse click frequency and accuracy
- **Interactive Game**: Engaging target-clicking game for data collection

#### 3. Facial Expression Analysis
- **Blink Rate**: Eye blink frequency monitoring
- **Eye Closure Duration**: Microsleep detection
- **Facial Expression**: Emotion and alertness recognition
- **Camera Integration**: Real-time webcam analysis

### Machine Learning Integration
- **Ensemble Model**: Combines multiple data sources for accurate prediction
- **Confidence Scoring**: Provides reliability metrics for predictions
- **Personalized Recommendations**: Tailored suggestions based on fatigue level
- **Data Quality Assessment**: Evaluates the reliability of collected data

## 🛠 Technology Stack

### Backend
- **Django 4.2**: Web framework
- **Python 3.8+**: Core programming language
- **NumPy**: Numerical computations
- **Scikit-learn**: Machine learning algorithms
- **Pandas**: Data manipulation and analysis

### Frontend
- **HTML5/CSS3**: Modern web standards
- **Bootstrap 5**: Responsive UI framework
- **JavaScript ES6+**: Interactive functionality
- **Chart.js**: Data visualization
- **WebRTC**: Camera access for facial analysis

### Machine Learning
- **TensorFlow/Keras**: Deep learning models
- **OpenCV**: Computer vision processing
- **MediaPipe**: Facial landmark detection
- **Custom ML Pipeline**: Fatigue prediction algorithms

## 📦 Installation

### Prerequisites
- Python 3.8 or higher
- pip (Python package installer)
- Modern web browser with camera support

### Setup Instructions

1. **Clone the Repository**
   ```bash
   git clone <repository-url>
   cd mental_fatique
   ```

2. **Create Virtual Environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run Database Migrations**
   ```bash
   python manage.py migrate
   ```

5. **Start Development Server**
   ```bash
   python manage.py runserver
   ```

6. **Access the Application**
   Open your browser and navigate to `http://127.0.0.1:8000/`

## 🎯 Usage Guide

### Complete Testing Flow

1. **Home Page** (http://127.0.0.1:8000/)
   - Click "Get Started" to begin the data collection process

2. **Data Collection Process** (http://127.0.0.1:8000/data_collection/)
   - **Step 1: Introduction** - Click "Begin Data Collection" to start
   - **Step 2: Typing Pattern Analysis** - Type the provided text to analyze your typing patterns
   - **Step 3: Mouse Movement Analysis** - Play the target-clicking game to test reaction time
   - **Step 4: Facial Analysis** - Allow camera access to analyze facial expressions
   - **Step 5: Results** - View your calculated fatigue level and click "View Dashboard"

3. **Dashboard** (http://127.0.0.1:8000/dashboard/view/)
   - View your personalized fatigue analysis based on collected data
   - See ML-powered insights and recommendations
   - Track individual component scores

### What's Working Now

✅ **Complete Data Collection Flow** - All steps work seamlessly
✅ **Typing Pattern Analysis** - Captures typing speed, error rate, and pause frequency
✅ **Mouse Movement Analysis** - Interactive target-clicking game with reaction time measurement
✅ **Facial Analysis** - Simulates facial expression and eye movement analysis
✅ **ML Model Integration** - Real machine learning models analyze the collected data
✅ **Dynamic Dashboard** - Results display with ML-enhanced insights
✅ **Session Storage** - Data persists between pages
✅ **API Integration** - Backend ML analysis via REST API

## 🧠 Machine Learning Models

The system includes a comprehensive ML pipeline located in `ml_models/fatigue_predictor.py`:

### Fatigue Prediction Algorithm
- **Multi-Modal Analysis**: Combines typing, mouse, and facial data
- **Feature Normalization**: Z-score normalization for consistent scaling
- **Weighted Ensemble**: Intelligent combination of individual predictions
- **Confidence Estimation**: Reliability metrics for predictions

### API Endpoints
- `POST /api/fatigue/analyze/`: Submit collected data for ML analysis
- `GET /api/fatigue/insights/`: Get personalized recommendations

## 🔧 Project Structure

```
mental_fatique/
├── ml_models/
│   └── fatigue_predictor.py      # ML models and algorithms
├── fatigue_analysis/
│   ├── views.py                  # API endpoints for ML integration
│   └── urls.py                   # URL routing for API
├── templates/
│   ├── index.html                # Home page
│   ├── data_collection.html      # Complete data collection flow
│   └── dashboard/
│       └── index.html            # ML-enhanced dashboard
├── static/                       # CSS, JS, and image assets
├── requirements.txt              # Python dependencies
└── manage.py                     # Django management script
```

## 🚀 Key Features Implemented

### 1. Complete Data Collection Pipeline
- **Step-by-step process**: Guided user experience
- **Real-time feedback**: Live metrics during data collection
- **Progress tracking**: Visual progress indicators
- **Skip options**: Flexible data collection

### 2. Machine Learning Integration
- **Custom ML models**: Purpose-built fatigue detection algorithms
- **API integration**: RESTful endpoints for analysis
- **Real-time processing**: Immediate results after data collection
- **Confidence scoring**: Reliability metrics for predictions

### 3. Dynamic Dashboard
- **ML-powered insights**: Enhanced analysis using collected data
- **Personalized recommendations**: Tailored suggestions based on fatigue level
- **Data quality indicators**: Assessment of input data reliability
- **Interactive visualizations**: Charts and graphs for data representation

### 4. Multi-Modal Analysis
- **Typing patterns**: Speed, accuracy, and rhythm analysis
- **Mouse movements**: Reaction time and precision measurement
- **Facial analysis**: Expression and eye movement detection
- **Combined scoring**: Intelligent fusion of all data sources

## 📊 How It Works

1. **Data Collection**: User completes typing, mouse, and facial analysis tests
2. **ML Processing**: Collected data is sent to ML models via API
3. **Analysis**: Machine learning algorithms analyze patterns and predict fatigue
4. **Insights**: Personalized recommendations and insights are generated
5. **Dashboard**: Results are displayed with dynamic, data-driven content

## 🔒 Privacy & Security

- **Local Processing**: All analysis happens on your device
- **Session-Based**: Data cleared when session ends
- **No Permanent Storage**: Personal data is not saved long-term
- **Camera Privacy**: Video data processed locally only

## 🎯 Testing the Application

1. **Start the server**: `python manage.py runserver`
2. **Open browser**: Navigate to `http://127.0.0.1:8000/`
3. **Complete the flow**:
   - Click "Get Started"
   - Complete typing test
   - Play mouse game
   - Allow camera for facial analysis
   - View ML-enhanced results in dashboard

---

**Mental Fatigue Detector** - AI-powered analysis for better productivity and well-being.
