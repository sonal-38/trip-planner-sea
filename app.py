from __future__ import annotations

from typing import Any

import streamlit as st

from storage import save_itinerary
from travel_agents import generate_travel_plan

st.set_page_config(page_title="Dream Trip Planner", page_icon="🏝️", layout="wide")

PAGE_CSS = """
<style>
    .stApp {
        background:
            radial-gradient(circle at top left, rgba(14, 165, 233, 0.08), transparent 26%),
            radial-gradient(circle at top right, rgba(20, 184, 166, 0.08), transparent 20%),
            linear-gradient(180deg, #fcfcfa 0%, #ffffff 100%);
        color: #0f172a;
    }
    .main-wrap {
        max-width: 1080px;
        margin: 0 auto;
        padding: 0.75rem 0 2rem;
    }
    .hero {
        text-align: center;
        margin: 0.25rem 0 1rem;
    }
    .hero h1 {
        font-size: clamp(2rem, 4vw, 3.35rem);
        font-weight: 800;
        line-height: 1.05;
        letter-spacing: -0.04em;
        margin-bottom: 0.3rem;
    }
    .hero h1 .accent {
        color: #0f9aa8;
    }
    .hero p {
        color: #475569;
        font-size: 0.98rem;
        max-width: 720px;
        margin: 0 auto;
    }
    .stepper {
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 0.55rem;
        margin: 1rem 0 1.1rem;
    }
    .step-circle {
        width: 40px;
        height: 40px;
        border-radius: 999px;
        display: grid;
        place-items: center;
        font-weight: 700;
        box-shadow: 0 8px 18px rgba(15, 23, 42, 0.08);
    }
    .step-circle.done {
        background: #0f9aa8;
        color: white;
    }
    .step-circle.active {
        background: #0f9aa8;
        color: white;
        outline: 5px solid rgba(15, 154, 168, 0.18);
    }
    .step-circle.waiting {
        background: #f4efe4;
        color: #a3a3a3;
    }
    .step-line {
        width: min(8vw, 58px);
        height: 2px;
        background: #d8edea;
        border-radius: 999px;
    }
    .panel {
        background: rgba(255, 255, 255, 0.92);
        border: 1px solid rgba(15, 154, 168, 0.10);
        border-radius: 18px;
        box-shadow: 0 18px 36px rgba(15, 23, 42, 0.08);
        padding: 0.9rem 1.2rem 1rem;
        margin-bottom: 1rem;
    }
    .panel h2 {
        # Trivial change for git push
        .result-box {
            background: linear-gradient(180deg, rgba(15, 154, 168, 0.06), rgba(15, 154, 168, 0.02));
        margin: 0.25rem 0 0.15rem;
        text-align: center;
        font-size: 1.35rem;
    }
    .panel p.sub {
        text-align: center;
        color: #64748b;
        margin: 0 0 0.9rem;
    }
    .soft-divider {
        height: 1px;
        background: rgba(15, 23, 42, 0.08);
        margin: 1rem 0;
    }
    .output-card {
        background: #ffffff;
        border: 1px solid rgba(15, 154, 168, 0.14);
        border-radius: 18px;
        box-shadow: 0 10px 22px rgba(15, 23, 42, 0.06);
        padding: 1rem 1rem 0.95rem;
        height: 100%;
    }
    .output-card h3 {
        margin: 0;
        font-size: 1.02rem;
    }
    .output-card .summary {
        color: #334155;
        margin: 0.5rem 0 0.65rem;
        line-height: 1.5;
    }
    .pill {
        display: inline-block;
        background: #eefbf7;
        color: #047857;
        border-radius: 999px;
        padding: 0.25rem 0.65rem;
        font-size: 0.8rem;
        margin: 0.15rem 0.25rem 0.15rem 0;
    }
    .result-box {
        background: linear-gradient(180deg, rgba(15, 154, 168, 0.06), rgba(15, 154, 168, 0.02));
        border: 1px solid rgba(15, 154, 168, 0.15);
        border-radius: 18px;
        padding: 1rem 1rem 0.2rem;
    }
    .choice-label {
        font-size: 0.82rem;
        color: #64748b;
        margin-bottom: 0.35rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.06em;
    }
    div[data-baseweb="select"] > div,
    div[data-baseweb="input"] > div {
        border-radius: 14px !important;
        border-color: rgba(15, 154, 168, 0.18) !important;
        min-height: 46px;
    }
</style>
"""


def _icon_for_step(step: int, active_step: int) -> str:
    if step < active_step:
        return "✓"
    if step == active_step:
        return str(step)
    return str(step)


def render_stepper(active_step: int) -> None:
    cols = st.columns([1, 1, 1, 1, 1, 1, 1])
    with cols[1]:
        st.markdown(
            f'<div class="step-circle {"done" if active_step > 1 else "active" if active_step == 1 else "waiting"}">{_icon_for_step(1, active_step)}</div>',
            unsafe_allow_html=True,
        )
    with cols[2]:
        st.markdown('<div class="step-line"></div>', unsafe_allow_html=True)
    with cols[3]:
        st.markdown(
            f'<div class="step-circle {"done" if active_step > 2 else "active" if active_step == 2 else "waiting"}">{_icon_for_step(2, active_step)}</div>',
            unsafe_allow_html=True,
        )
    with cols[4]:
        st.markdown('<div class="step-line"></div>', unsafe_allow_html=True)
    with cols[5]:
        st.markdown(
            f'<div class="step-circle {"active" if active_step == 3 else "waiting"}">{_icon_for_step(3, active_step)}</div>',
            unsafe_allow_html=True,
        )


def render_output_card(title: str, payload: dict[str, Any]) -> None:
    bullets = payload.get("bullets", [])
    st.markdown(f"<div class='output-card'><h3>{title}</h3><p class='summary'>{payload.get('summary', '')}</p>", unsafe_allow_html=True)
    for bullet in bullets:
        st.markdown(f"<span class='pill'>{bullet}</span>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)


def main() -> None:
    st.markdown(PAGE_CSS, unsafe_allow_html=True)
    st.markdown("<div class='main-wrap'>", unsafe_allow_html=True)

    st.markdown(
        """
        <div class="hero">
            <h1>Plan Your Dream Trip to <span class="accent">Anywhere</span> 🏝️</h1>
            <p>Pick the destination and three simple trip preferences. The agents will turn them into a clean plan, then combine everything into a local itinerary.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if "active_step" not in st.session_state:
        st.session_state.active_step = 1
    if "results" not in st.session_state:
        st.session_state.results = None
    if "last_error" not in st.session_state:
        st.session_state.last_error = ""

    render_stepper(st.session_state.active_step)

    destination = st.text_input("Where do you want to go?", placeholder="Enter a city, region, or country")

    st.markdown('<div class="panel">', unsafe_allow_html=True)
    st.markdown("<h2>Trip Preferences</h2>", unsafe_allow_html=True)
    st.markdown("<p class='sub'>Keep it simple: month, duration, food preference, and budget.</p>", unsafe_allow_html=True)

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown('<div class="choice-label">Travel month</div>', unsafe_allow_html=True)
        month = st.selectbox(
            "Travel month",
            [
                "January",
                "February",
                "March",
                "April",
                "May",
                "June",
                "July",
                "August",
                "September",
                "October",
                "November",
                "December",
            ],
            index=0,
            label_visibility="collapsed",
        )
    with c2:
        st.markdown('<div class="choice-label">Duration</div>', unsafe_allow_html=True)
        duration = st.select_slider(
            "Duration",
            options=[2, 3, 4, 5, 6, 7],
            value=3,
            label_visibility="collapsed",
        )
    with c3:
        st.markdown('<div class="choice-label">Food preference</div>', unsafe_allow_html=True)
        food_preference = st.selectbox(
            "Food preference",
            ["Vegetarian", "Non-Vegetarian", "Both"],
            index=2,
            label_visibility="collapsed",
        )
    with c4:
        st.markdown('<div class="choice-label">Budget</div>', unsafe_allow_html=True)
        budget = st.selectbox(
            "Budget",
            ["Budget", "Mid-range", "Premium"],
            index=1,
            label_visibility="collapsed",
        )

    action_col1, action_col2 = st.columns([1, 1])
    with action_col1:
        should_generate = st.button("Generate 2 Agent Outputs", use_container_width=True, type="primary")
    with action_col2:
        save_only = st.button("Save Final Itinerary", use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

    if should_generate:
        if not destination.strip():
            st.warning("Enter a destination first.")
        else:
            st.session_state.active_step = 3
            try:
                with st.spinner("Agents are working..."):
                    results = generate_travel_plan(
                        destination=destination.strip(),
                        month=month,
                        duration=int(duration),
                        budget=budget.lower(),
                        food_preference=food_preference.lower(),
                    )
                st.session_state.results = results
                st.session_state.last_error = ""
                st.success("Agent outputs are ready.")
            except Exception as exc:
                message = str(exc)
                st.session_state.last_error = message
                if "503" in message or "UNAVAILABLE" in message:
                    st.error("Gemini is temporarily overloaded (503). Please retry in a few moments.")
                elif "429" in message or "RESOURCE_EXHAUSTED" in message:
                    st.error("Gemini quota or rate limit reached (429). Check billing/quota or retry later.")
                else:
                    st.error(f"Failed to generate plan: {message}")

    if st.session_state.last_error:
        st.markdown("### Last Error")
        st.code(st.session_state.last_error)

    if save_only and st.session_state.results:
        path = save_itinerary(st.session_state.results.get("itinerary", {}))
        st.info(f"Saved locally to {path.name}")
    elif save_only:
        st.warning("Generate a plan before saving.")

    results = st.session_state.results
    if results:
        st.markdown('<div class="soft-divider"></div>', unsafe_allow_html=True)
        st.subheader("Two Agent Outputs")
        cards = st.columns(2)
        with cards[0]:
            render_output_card("Agent 1 - Weather", results.get("agent_one", {}))
        with cards[1]:
            render_output_card("Agent 2 - Hotel", results.get("agent_two", {}))

        st.markdown('<div class="soft-divider"></div>', unsafe_allow_html=True)
        st.subheader("Generated Itinerary")
        itinerary = results.get("itinerary", {})
        st.markdown(
            f"""
            <div class="result-box">
                <p><strong>Destination:</strong> {itinerary.get('destination', '')}</p>
                <p><strong>Month:</strong> {itinerary.get('month', '')}</p>
                <p><strong>Duration:</strong> {itinerary.get('duration', '')} days</p>
                <p><strong>Food preference:</strong> {itinerary.get('food_preference', '')}</p>
                <p><strong>Budget:</strong> {itinerary.get('budget', '')}</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

        weather = itinerary.get("weather", {})
        if weather:
            st.markdown(
                f"""
                <div class="result-box" style="margin-top:0.6rem;">
                    <p><strong>Weather:</strong> {weather.get('condition', '')}</p>
                    <p><strong>Temperature:</strong> {weather.get('temperature', '')}</p>
                    <p><strong>Humidity:</strong> {weather.get('humidity', '')}</p>
                    <p><strong>Wind:</strong> {weather.get('wind', '')}</p>
                </div>
                """,
                unsafe_allow_html=True,
            )

        packing = itinerary.get("packing_suggestions", [])
        if packing:
            st.markdown("### Packing Suggestions")
            for item in packing:
                st.markdown(f"- {item}")

        hotel_options = itinerary.get("hotel_options", [])
        if hotel_options:
            st.markdown("### Hotel Options")
            for item in hotel_options:
                st.markdown(f"- {item}")

        days = itinerary.get("days", [])
        for day in days:
            with st.container(border=True):
                st.markdown(
                    f"<div style='display:flex;align-items:center;gap:0.8rem;margin-bottom:0.35rem;'><div style='width:34px;height:34px;border-radius:999px;background:#0f9aa8;color:white;display:grid;place-items:center;font-weight:700;'>D{day.get('day', '')}</div><div><div style='font-weight:800;'>{day.get('title', '')}</div><div style='color:#64748b;font-size:0.82rem;'>Day {day.get('day', '')} of {len(days)}</div></div></div>",
                    unsafe_allow_html=True,
                )
                mc1, mc2, mc3 = st.columns(3)
                with mc1:
                    st.markdown(f"**Morning**  \n{day.get('morning', '')}")
                with mc2:
                    st.markdown(f"**Afternoon**  \n{day.get('afternoon', '')}")
                with mc3:
                    st.markdown(f"**Evening**  \n{day.get('evening', '')}")

        if st.button("Generate and Store Final Itinerary", type="secondary"):
            path = save_itinerary(itinerary)
            st.success(f"Final itinerary saved locally at {path.name}")

    st.markdown("<div style='height: 0.5rem;'></div>", unsafe_allow_html=True)
    st.caption("Stored itineraries live in the local data folder and can be reused in later sessions.")
    st.markdown("</div>", unsafe_allow_html=True)


if __name__ == "__main__":
    main()
