# AI-Powered Mental Fatigue Detector & Productivity Booster

A comprehensive system that monitors user behavior to detect mental fatigue and provide productivity recommendations.

## Team Members
- Siddhi Lahoti
- Yashodhan Suryawanshi
- Indrakant
- Lokesh

---

## Project Overview
This system combines multiple data sources to detect mental fatigue and boost productivity:

- **Behavioral Data Collection**
  - Typing patterns
  - Mouse movements
  - Facial expressions
  - Voice analysis

- **Mental Fatigue Detection**
  - Machine learning models for fatigue prediction
  - Real-time analysis of behavioral patterns

- **Productivity Recommendations**
  - Personalized suggestions based on user state
  - Reinforcement learning for optimal recommendations

- **Real-time Dashboard**
  - Live monitoring of user state
  - Interactive visualizations
  - Productivity insights

---

## Tech Stack
- **Backend**: Django
- **Machine Learning**: TensorFlow/Keras
- **Computer Vision**: OpenCV
- **Frontend**: HTML/CSS
- **Analytics**: Power BI
- **Database**: SQLite

---

## 📸 Project Screenshots  

### 🏠 Home Page
![Home](Project%20Images/home.png)

### 📊 Dashboard
![Dashboard](Project%20Images/dashboard.png)

### 📝 Data Collection
![Data Collection 1](Project%20Images/datacollection1.png)  
![Data Collection 2](Project%20Images/datacollection2%20(3).png)  
![Data Collection 3](Project%20Images/datacollection3.png)

### ✅ Results
![Result](Project%20Images/result.png)

---

## Setup Instructions
1. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Run migrations:
   ```bash
   python manage.py migrate
   ```

4. Start the development server:
   ```bash
   python manage.py runserver
   ```

## Project Structure
```
fatigue_detector/
├── core/                 # Main Django project
├── data_collection/      # Data collection modules
├── ml_models/           # Machine learning models
├── dashboard/           # Frontend dashboard
├── analytics/           # Analytics and reporting
└── utils/              # Utility functions
```

## License
MIT License 
