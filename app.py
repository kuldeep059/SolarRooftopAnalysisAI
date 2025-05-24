import streamlit as st
import os
from dotenv import load_dotenv
from openai import OpenAI
import base64
import io
import json
import math

# --- Load API Key from .env ---
load_dotenv()
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

# --- Initialize OpenRouter Client ---
# The base_url needs to point to OpenRouter for their API
# Note: If OpenRouter changes their base_url in the future, you'd update it here.
client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=OPENROUTER_API_KEY,
)

# --- Hypothetical Solar Data (Context Management) ---
# These values are illustrative and would be loaded from a database or more precise APIs in a real app
PANEL_WATTAGE = 400 # Watts per panel
PANEL_AREA_SQ_FT = 18 # Approximate area per panel in square feet (e.g., 6.5ft x 2.75ft)
PANEL_COST_PER_WATT = 70.00 # Average cost per watt (INR) - this is an all-in cost for panels, inverter, installation
AVG_ELECTRICITY_RATE_PER_KWH = 6.50 # Average electricity rate (INR per kWh)
SYSTEM_LIFESPAN_YEARS = 25 # Typical lifespan for ROI calculation

# --- Function to encode image to base64 for AI ---
def encode_image(uploaded_file):
    # Read the file into bytes
    bytes_data = uploaded_file.getvalue()
    # Encode bytes to base64 string
    return base64.b64encode(bytes_data).decode('utf-8')

# --- Function to call Vision AI for analysis and get JSON output ---
def get_roof_analysis_from_ai(image_base64):
    try:
        response = client.chat.completions.create(
            model="openai/gpt-4o", # Using GPT-4o which has Vision capabilities
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": """Analyze this satellite image of a rooftop for solar panel installation potential.
                        Identify the main rooftop area, approximate shape, and detect any significant obstructions like chimneys, vents, skylights, or trees casting shadows.
                        Provide a qualitative assessment of sunlight exposure.
                        Estimate the approximate usable area for solar panels qualitatively (e.g., "small", "medium", "large").
                        Output the analysis in a JSON format with the following keys:
                        - "roof_shape": (e.g., "rectangular", "L-shaped", "complex")
                        - "main_obstacles": (list of strings, e.g., ["chimney", "vent", "tree shading"])
                        - "sunlight_exposure": (e.g., "excellent", "good", "moderate", "poor - significant shading")
                        - "usable_area_qualitative": (e.g., "small", "medium", "large")
                        - "overall_assessment": (a concise summary string)
                        Ensure the output is valid JSON, starting and ending with curly braces `{}`.
                        """},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{image_base64}"
                            },
                        },
                    ],
                }
            ],
            max_tokens=500, # Limit the response length
            response_format={"type": "json_object"} # Crucial for getting JSON output
        )
        # Extract the content and attempt to parse it as JSON
        ai_content = response.choices[0].message.content
        return json.loads(ai_content) # Parse the JSON string into a Python dictionary
    except json.JSONDecodeError as e:
        st.error(f"Failed to parse AI response as JSON: {e}. Raw response: {response.choices[0].message.content}")
        return {"error": f"JSON parsing error: {e}", "raw_response": response.choices[0].message.content}
    except Exception as e:
        return {"error": f"Error during AI analysis: {e}"}

# --- Function for Simplified Calculations ---
def perform_simplified_calculations(ai_analysis):
    usable_area_qualitative = ai_analysis.get('usable_area_qualitative', 'N/A').lower()
    sunlight_exposure = ai_analysis.get('sunlight_exposure', 'N/A').lower()

    # Simple mapping of qualitative area to estimated square footage
    if "large" in usable_area_qualitative:
        estimated_usable_sq_ft = 600
    elif "medium" in usable_area_qualitative:
        estimated_usable_sq_ft = 300
    elif "small" in usable_area_qualitative:
        estimated_usable_sq_ft = 100
    else:
        estimated_usable_sq_ft = 0 # Default if unknown

    # Calculate estimated number of panels
    if estimated_usable_sq_ft > 0:
        estimated_panel_count = math.floor(estimated_usable_sq_ft / PANEL_AREA_SQ_FT)
    else:
        estimated_panel_count = 0

    # Calculate estimated total system wattage
    estimated_system_wattage = estimated_panel_count * PANEL_WATTAGE

    # Adjust production based on sunlight exposure (very simplified)
    production_factor = 1.0 # default for 'good'
    if "excellent" in sunlight_exposure:
        production_factor = 1.2
    elif "moderate" in sunlight_exposure:
        production_factor = 0.8
    elif "poor" in sunlight_exposure or "significant shading" in sunlight_exposure:
        production_factor = 0.5 # significantly reduced

    # Estimated yearly energy production (kWh)
    # Assuming a system produces ~1.3-1.6 kWh per watt-peak per year in good conditions (simplified)
    # Using 1.4 as a base average for demonstration, adjusted by production_factor
    estimated_yearly_kwh = (estimated_system_wattage * 1.4 * production_factor) / 1000 if estimated_system_wattage > 0 else 0

    # Calculate estimated system cost
    estimated_system_cost = (estimated_system_wattage / 1000) * PANEL_COST_PER_WATT * 1000 if estimated_system_wattage > 0 else 0 # Convert to kW for cost

    # Calculate estimated yearly savings
    estimated_yearly_savings = estimated_yearly_kwh * AVG_ELECTRICITY_RATE_PER_KWH

    # Calculate simplified ROI (payback period)
    if estimated_yearly_savings > 0:
        estimated_roi_years = estimated_system_cost / estimated_yearly_savings
    else:
        estimated_roi_years = "N/A (No significant savings)"

    return {
        "estimated_usable_sq_ft": estimated_usable_sq_ft,
        "estimated_panel_count": estimated_panel_count,
        "estimated_system_wattage": estimated_system_wattage,
        "estimated_yearly_kwh": estimated_yearly_kwh,
        "estimated_system_cost": estimated_system_cost,
        "estimated_yearly_savings": estimated_yearly_savings,
        "estimated_roi_years": estimated_roi_years,
    }

def main():
    st.set_page_config(page_title="Rooftop Solar Analysis", layout="wide")
    st.write("WattMonk Assignment - AI-Powered Rooftop Solar Analysis Tool")
    st.title("☀️ AI-Powered Rooftop Solar Analysis Tool")
    st.write("Upload a satellite image of a rooftop to assess its solar potential.")

    uploaded_file = st.file_uploader("Choose a satellite image...", type=["jpg", "jpeg", "png"])

    if uploaded_file is not None:
        st.image(uploaded_file, caption="Uploaded Satellite Image.", use_container_width=True)
        st.success("Image uploaded successfully!")
        st.info("Initiating solar analysis...")

        image_base64 = encode_image(uploaded_file)

        with st.spinner("Analyzing rooftop with AI... This may take a moment."):
            ai_analysis_result = get_roof_analysis_from_ai(image_base64) # This will now be a dictionary

            st.subheader("AI-Powered Rooftop Analysis:")

            if "error" in ai_analysis_result:
                st.error(f"Analysis failed: {ai_analysis_result['error']}")
                if "raw_response" in ai_analysis_result:
                    st.text("Raw AI Response (for debugging):")
                    st.code(ai_analysis_result['raw_response'])
            else:
                # Display the structured results from AI
                st.write(f"**Roof Shape:** {ai_analysis_result.get('roof_shape', 'N/A')}")
                st.write(f"**Main Obstacles:** {', '.join(ai_analysis_result.get('main_obstacles', ['None']))}")
                st.write(f"**Sunlight Exposure:** {ai_analysis_result.get('sunlight_exposure', 'N/A').capitalize()}")
                st.write(f"**Usable Area (Qualitative):** {ai_analysis_result.get('usable_area_qualitative', 'N/A').capitalize()}")
                st.write(f"**Overall Assessment:** {ai_analysis_result.get('overall_assessment', 'N/A')}")

                st.subheader("Simplified Solar Potential Estimates:")
                # Perform and display simplified calculations
                calculations = perform_simplified_calculations(ai_analysis_result)

                st.write(f"- **Estimated Usable Roof Area:** {calculations['estimated_usable_sq_ft']:.0f} sq ft")
                st.write(f"- **Estimated Optimal Panel Count:** {calculations['estimated_panel_count']}")
                st.write(f"- **Estimated System Size:** {calculations['estimated_system_wattage'] / 1000:.2f} kW")
                st.write(f"- **Estimated Yearly Energy Production:** {calculations['estimated_yearly_kwh']:.0f} kWh")
                st.write(f"- **Estimated System Cost:** ₹{calculations['estimated_system_cost']:.2f}")
                st.write(f"- **Estimated Yearly Savings:** ₹{calculations['estimated_yearly_savings']:.2f}")
                st.write(f"- **Estimated ROI (Payback Period):** {calculations['estimated_roi_years']:.1f} years" if isinstance(calculations['estimated_roi_years'], (int, float)) else calculations['estimated_roi_years'])


                st.write("\n---")
                st.write("**Important Note on Estimates:**")
                st.write("These calculations are simplified and based on hypothetical averages and qualitative AI assessments. For precise figures, a real-world tool would require:")
                st.write("- Exact roof dimensions and angles (from precise image processing or CAD data).")
                st.write("- Detailed local solar irradiance data (from geographical APIs).")
                st.write("- Real-time local electricity rates and incentive programs.")
                st.write("- Specific solar panel models and up-to-date installation costs.")


if __name__ == "__main__":
    main()