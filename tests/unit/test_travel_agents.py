from __future__ import annotations

import json

import pytest

import travel_agents


class _FakeResponse:
    def __init__(self, payload: dict):
        self.text = json.dumps(payload)


class _FakeModels:
    def generate_content(self, model: str, contents: str, config: dict):
        if "Weather Agent" in contents:
            return _FakeResponse(
                {
                    "summary": "Pleasant weather expected with light breeze.",
                    "bullets": [
                        "Temperature around 24-31C.",
                        "Humidity moderate in evenings.",
                        "Carry light cotton outfits.",
                    ],
                }
            )

        return _FakeResponse(
            {
                "summary": "Good hotel picks in selected budget and a practical 3-day itinerary.",
                "hotel_options": [
                    "Palm Residency - 5500/night",
                    "Bay View Hotel - 6200/night",
                    "Garden Stay - 4800/night",
                ],
                "bullets": [
                    "Near key city attractions.",
                    "Breakfast included in most options.",
                    "Budget aligned with selected range.",
                ],
                "itinerary": {
                    "destination": "Goa",
                    "month": "November",
                    "duration": 3,
                    "food_preference": "both",
                    "budget": "mid-range",
                    "weather": {
                        "condition": "Pleasant",
                        "temperature": "24-31C",
                        "humidity": "65%",
                        "wind": "8 km/h",
                    },
                    "packing_suggestions": [
                        "Light cotton shirts",
                        "Comfortable walking shoes",
                        "Sunscreen and hat",
                    ],
                    "hotel_options": [
                        "Palm Residency - 5500/night",
                        "Bay View Hotel - 6200/night",
                        "Garden Stay - 4800/night",
                    ],
                    "days": [
                        {
                            "day": 1,
                            "title": "Day 1: Beaches",
                            "morning": "Beach walk",
                            "afternoon": "Lunch and fort",
                            "evening": "Market and dinner",
                        },
                        {
                            "day": 2,
                            "title": "Day 2: Culture",
                            "morning": "Church visit",
                            "afternoon": "Old town tour",
                            "evening": "River cruise",
                        },
                        {
                            "day": 3,
                            "title": "Day 3: Leisure",
                            "morning": "Cafe trail",
                            "afternoon": "Shopping",
                            "evening": "Sunset dinner",
                        },
                    ],
                },
            }
        )


class _FakeClient:
    def __init__(self):
        self.models = _FakeModels()


def test_extract_json_parses_valid_payload():
    payload = travel_agents._extract_json('{"summary":"ok","bullets":["a","b","c"]}')
    assert payload is not None
    assert payload["summary"] == "ok"


def test_generate_plan_contract(monkeypatch):
    monkeypatch.setattr(travel_agents, "_get_gemini_client", lambda: _FakeClient())

    result = travel_agents.generate_travel_plan(
        destination="Goa",
        month="November",
        duration=3,
        budget="mid-range",
        food_preference="both",
    )

    assert "agent_one" in result
    assert "agent_two" in result
    assert "itinerary" in result

    assert result["agent_one"]["title"] == "Weather Agent"
    assert result["agent_two"]["title"] == "Hotel Agent"
    assert len(result["agent_one"]["bullets"]) >= 3
    assert len(result["agent_two"]["bullets"]) >= 3

    itinerary = result["itinerary"]
    assert itinerary["destination"] == "Goa"
    assert itinerary["duration"] == 3
    assert len(itinerary["days"]) == 3
    assert len(itinerary["hotel_options"]) >= 3


def test_raises_when_client_missing(monkeypatch):
    monkeypatch.setattr(travel_agents, "_get_gemini_client", lambda: None)

    with pytest.raises(ValueError):
        travel_agents.generate_travel_plan(
            destination="Goa",
            month="November",
            duration=3,
            budget="mid-range",
            food_preference="both",
        )
