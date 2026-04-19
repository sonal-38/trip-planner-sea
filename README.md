# Dream Trip Planner

A Streamlit app that lets a user enter any destination, run a 3-agent LangGraph workflow, and store a combined itinerary locally.

## Features

- One-page UI inspired by the provided travel planner screenshot
- Destination input for any city, region, or country
- Three agents: Weather, Hotel, and Itinerary Generator
- Optional Gemini API integration for agent outputs (fallback works without API key)
- Local itinerary storage as JSON
- Reusable generated itineraries in the `data/itineraries` folder

## Run

```bash
pip install -r requirements.txt
streamlit run app.py
```

## Storage

Generated itineraries are written to `data/itineraries/`.
