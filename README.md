# SpeedLimit

Sets the speed limit on a highway based on light, road conditions and air quality. When everything looks fine, it stays at 80 km/h.

Software Engineering course project by Cristian and Morgan.

## Run

```
python -m venv .venv
.venv\Scripts\pip install -r requirements.txt
.venv\Scripts\streamlit run app/main.py
```

The app needs a Gemini API key in a `.env` file: `GEMINI_API_KEY=your-key`. Every decision is logged to `logs/decisions.csv`.

## Train the network

```
.venv\Scripts\python training/train.py
```

This cleans the data (`training/clean.py`), trains the network on the dark or icy hours of Year N and saves it to `models/network.joblib`, with its test results in `models/metrics.json`. A trained network is already in the repo, so the app runs without this step.
