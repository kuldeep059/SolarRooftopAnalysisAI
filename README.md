
# Solar Rooftop Analysis AI Assistant

## Overview

This project implements an AI-powered rooftop analysis tool designed to assess solar installation potential from satellite imagery. It aims to provide accurate solar potential assessments, installation recommendations, and ROI estimates for both homeowners and solar professionals. This system demonstrates the integration of multiple AI services to solve a critical challenge within the solar industry.

## Project Goal

The primary goal of this intelligent system is to analyze any rooftop from satellite imagery and deliver comprehensive solar potential assessments, including:
* Estimated number of solar panels that can be installed.
* Annual energy production estimates.
* Projected installation costs.
* Potential electricity bill savings.
* Return on Investment (ROI) estimates.

## Features

* **Satellite Image Upload:** Users can upload a satellite image of a rooftop.
* **AI-Powered Analysis:** Leverages Vision AI (GPT-4o via OpenRouter) to interpret the rooftop's characteristics, including size, shape, obstructions, and sun exposure.
* **Structured Output Extraction:** Utilizes prompt engineering to extract structured JSON output from the LLM, making the AI's analysis easily parsable.
* **Solar Potential Calculations:** Performs simplified calculations for panel count, energy production, cost, savings, and ROI based on the AI's insights and hypothetical industry data.
* **User-Friendly Interface:** Built with Streamlit for an interactive web application.

## Required Knowledge Areas (Demonstrated)

This project touches upon various areas relevant to the solar industry and AI development:
* **Solar Panel Technology:** Implicitly considers types, efficiency, and specifications in calculations.
* **Cost & ROI Analysis:** Provides estimates based on typical industry pricing and payback periods.
* **LLM Integration:** Seamlessly integrates with a large language model (GPT-4o via OpenRouter API).
* **Prompt Engineering:** Employs effective prompt design to guide the LLM for structured and relevant output.
* **Web Interface Creation:** Utilizes Streamlit to build a dynamic and interactive web application.
* **Code Quality & Error Handling:** Structured code with basic error handling for robust performance.

## Project Setup Instructions (Local Development)

Follow these steps to set up and run the project on your local machine.

### Prerequisites

* Python 3.7+
* `pip` (Python package installer)
* Git

### Implementation


### 1. Clone the Repository

```bash
git clone [YOUR_GITHUB_REPO_URL]
cd solar_rooftop_analysis_tool # Or whatever your project folder is named
