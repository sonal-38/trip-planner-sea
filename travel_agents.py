from __future__ import annotations

from dataclasses import dataclass
import json
import os
from typing import Any

from dotenv import load_dotenv

try:
    from google import genai
except Exception:
    genai = None

load_dotenv()
GEMINI_MODEL_NAME = (os.getenv("GEMINI_MODEL", "gemini-2.0-flash") or "gemini-2.0-flash").strip()


@dataclass(frozen=True)
class AgentResult:
    title: str
    summary: str
    bullets: list[str]


MONTH_WEATHER = {
    "january": "Cool and mostly dry",
    "february": "Warm and comfortable",
    "march": "Warm transition season",
    "april": "Hot afternoons",
    "may": "Peak summer heat",
    "june": "Monsoon onset",
    "july": "Rainy season",
    "august": "Rainy season",
    "september": "Humid with improving weather",
    "october": "Pleasant post-monsoon",
    "november": "Pleasant and popular",
    "december": "Cool and peak travel",
}


def _normalized_model_name(model_name: str) -> str:
    if model_name.startswith("models/"):
        return model_name.split("/", 1)[1]
    return model_name


def _normalize_text(value: str) -> str:
    return value.strip() or "your destination"


def _month_weather(month: str) -> str:
    return MONTH_WEATHER.get(month.lower(), "Variable seasonal conditions")


def _budget_price_band(budget: str) -> str:
    if budget == "budget":
        return "INR 1,800-3,200 / night"
    if budget == "premium":
        return "INR 9,000-16,000 / night"
    return "INR 4,000-8,500 / night"


def _get_gemini_client() -> Any:
    key = os.getenv("GEMINI_API_KEY", "").strip()
    if not key or genai is None:
        return None
    return genai.Client(api_key=key)


def _extract_json(text: str) -> dict[str, Any] | None:
    raw = text.strip()
    if raw.startswith("```"):
        raw = raw.replace("```json", "").replace("```", "").strip()
    try:
        parsed = json.loads(raw)
        if isinstance(parsed, dict):
            return parsed
    except Exception:
        return None
    return None


class WeatherAgent:
    def __init__(self, client: Any):
        self.client = client

    def run(self, destination: str, month: str) -> dict[str, Any]:
        prompt = (
            "You are a Weather Agent for trip planning. Return JSON with keys summary and bullets. "
            "Bullets must include temperature trend, humidity/wind hint, and one travel caution."
            f"\nDestination: {destination}"
            f"\nMonth: {month}"
            f"\nSeason hint: {_month_weather(month)}"
        )
        response = self.client.models.generate_content(
            model=_normalized_model_name(GEMINI_MODEL_NAME),
            contents=prompt,
            config={
                "response_mime_type": "application/json",
                "response_schema": {
                    "type": "object",
                    "properties": {
                        "summary": {"type": "string"},
                        "hotel_options": {
                            "type": "array",
                            "items": {"type": "string"},
                            "minItems": 3,
                        },
                        "bullets": {
                            "type": "array",
                            "items": {"type": "string"},
                            "minItems": 3,
                            "maxItems": 5,
                        },
                    },
                    "required": ["summary", "bullets"],
                },
            },
        )
        payload = _extract_json(getattr(response, "text", "") or "")
        if not payload:
            raise RuntimeError("Weather Agent returned invalid JSON.")

        summary = str(payload.get("summary", "")).strip()
        bullets = payload.get("bullets", [])
        if not summary or not isinstance(bullets, list) or len(bullets) < 3:
            raise RuntimeError("Weather Agent response missing required fields.")

        normalized_bullets = [str(item).strip() for item in bullets if str(item).strip()][:5]
        return AgentResult("Weather Agent", summary, normalized_bullets).__dict__


class HotelAgent:
    def __init__(self, client: Any):
        self.client = client

    def run(
        self,
        destination: str,
        month: str,
        duration: int,
        budget: str,
        food_preference: str,
        weather_summary: str,
        weather_bullets: list[str],
    ) -> tuple[dict[str, Any], dict[str, Any]]:
        prompt = (
            "You are a Hotel Agent that also returns final trip itinerary. Return JSON with keys summary, bullets, itinerary. "
            "The itinerary must be practical and weather-aware, not generic."
            f"\nDestination: {destination}"
            f"\nMonth: {month}"
            f"\nDuration days: {duration}"
            f"\nBudget: {budget} ({_budget_price_band(budget)})"
            f"\nFood preference: {food_preference}"
            f"\nWeather agent summary: {weather_summary}"
            f"\nWeather agent bullets: {json.dumps(weather_bullets, ensure_ascii=True)}"
        )

        response = self.client.models.generate_content(
            model=_normalized_model_name(GEMINI_MODEL_NAME),
            contents=prompt,
            config={
                "response_mime_type": "application/json",
                "response_schema": {
                    "type": "object",
                    "properties": {
                        "summary": {"type": "string"},
                        "hotel_options": {
                            "type": "array",
                            "items": {"type": "string"},
                            "minItems": 3,
                        },
                        "bullets": {
                            "type": "array",
                            "items": {"type": "string"},
                            "minItems": 3,
                            "maxItems": 5,
                        },
                        "itinerary": {
                            "type": "object",
                            "properties": {
                                "destination": {"type": "string"},
                                "month": {"type": "string"},
                                "duration": {"type": "integer"},
                                "food_preference": {"type": "string"},
                                "budget": {"type": "string"},
                                "weather": {
                                    "type": "object",
                                    "properties": {
                                        "condition": {"type": "string"},
                                        "temperature": {"type": "string"},
                                        "humidity": {"type": "string"},
                                        "wind": {"type": "string"},
                                    },
                                    "required": ["condition", "temperature", "humidity", "wind"],
                                },
                                "packing_suggestions": {
                                    "type": "array",
                                    "items": {"type": "string"},
                                    "minItems": 3,
                                },
                                "hotel_options": {
                                    "type": "array",
                                    "items": {"type": "string"},
                                    "minItems": 3,
                                },
                                "days": {
                                    "type": "array",
                                    "items": {
                                        "type": "object",
                                        "properties": {
                                            "day": {"type": "integer"},
                                            "title": {"type": "string"},
                                            "morning": {"type": "string"},
                                            "afternoon": {"type": "string"},
                                            "evening": {"type": "string"},
                                        },
                                        "required": ["day", "title", "morning", "afternoon", "evening"],
                                    },
                                    "minItems": 1,
                                },
                            },
                            "required": [
                                "destination",
                                "month",
                                "duration",
                                "food_preference",
                                "budget",
                                "weather",
                                "packing_suggestions",
                                "hotel_options",
                                "days",
                            ],
                        },
                    },
                    "required": ["summary", "hotel_options", "bullets", "itinerary"],
                },
            },
        )

        payload = _extract_json(getattr(response, "text", "") or "")
        if not payload:
            raise RuntimeError("Hotel Agent returned invalid JSON.")

        summary = str(payload.get("summary", "")).strip()
        bullets = payload.get("bullets", [])
        hotel_options = payload.get("hotel_options", [])
        itinerary = payload.get("itinerary", {})

        if not summary or not isinstance(bullets, list) or len(bullets) < 3:
            raise RuntimeError("Hotel Agent summary/bullets missing.")
        if not isinstance(hotel_options, list):
            raise RuntimeError("Hotel Agent hotel options missing.")
        if not isinstance(itinerary, dict):
            raise RuntimeError("Hotel Agent itinerary missing.")

        days = itinerary.get("days", [])
        if not isinstance(days, list) or len(days) != int(duration):
            raise RuntimeError("Gemini itinerary day count does not match selected duration.")

        normalized_hotel_options = [str(item).strip() for item in hotel_options if str(item).strip()][:5]
        if len(normalized_hotel_options) < 3:
            # If model placed hotel options only in itinerary, pull them from there.
            itinerary_hotels = itinerary.get("hotel_options", [])
            normalized_hotel_options = [str(item).strip() for item in itinerary_hotels if str(item).strip()][:5]
        if len(normalized_hotel_options) < 3:
            raise RuntimeError("Hotel Agent must return at least 3 hotel options.")

        # Keep itinerary hotels consistent with what we render in the Hotel Agent output.
        itinerary["hotel_options"] = normalized_hotel_options

        normalized_bullets = [str(item).strip() for item in bullets if str(item).strip()][:5]
        hotel_bullets = normalized_bullets[:2] + [f"Hotel option: {item}" for item in normalized_hotel_options[:3]]
        hotel_result = AgentResult("Hotel Agent", summary, hotel_bullets[:5]).__dict__
        return hotel_result, itinerary


class TripPlanner:
    def __init__(self, client: Any):
        self.weather_agent = WeatherAgent(client)
        self.hotel_agent = HotelAgent(client)

    def plan_trip(self, destination: str, month: str, duration: int, budget: str, food_preference: str) -> dict[str, Any]:
        destination = _normalize_text(destination)
        weather_out = self.weather_agent.run(destination, month)
        hotel_out, itinerary = self.hotel_agent.run(
            destination=destination,
            month=month,
            duration=duration,
            budget=budget,
            food_preference=food_preference,
            weather_summary=weather_out["summary"],
            weather_bullets=weather_out["bullets"],
        )
        return {
            "agent_one": weather_out,
            "agent_two": hotel_out,
            "itinerary": itinerary,
        }


def generate_travel_plan(
    destination: str,
    month: str,
    duration: int,
    budget: str,
    food_preference: str,
) -> dict[str, Any]:
    client = _get_gemini_client()
    if client is None:
        raise ValueError("Set GEMINI_API_KEY in .env to generate the plan.")
    planner = TripPlanner(client)
    return planner.plan_trip(
        destination=destination,
        month=month,
        duration=duration,
        budget=budget,
        food_preference=food_preference,
    )
