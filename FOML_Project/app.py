from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import google.generativeai as genai
import traceback  # for better error printing

app = Flask(__name__)
CORS(app)

# Configure your Gemini API Key
genai.configure(api_key="AIzaSyAAiVdg-NtbsSNDiY_t_nNd-AzNBGLh_CY")

# Initialize Gemini model
model = genai.GenerativeModel(model_name="gemini-1.5-flash")

# Location to hospitals mapping
location_to_hospitals = {
    "chennai": [
        {"name": "Apollo Hospital", "location": "Chennai", "google_maps": "https://www.google.com/maps/search/?api=1&query=Apollo+Hospital+Chennai"},
        {"name": "Kauvery Hospital", "location": "Chennai", "google_maps": "https://www.google.com/maps/search/?api=1&query=Kauvery+Hospital+Chennai"},
        {"name": "Fortis Malar Hospital", "location": "Chennai", "google_maps": "https://www.google.com/maps/search/?api=1&query=Fortis+Malar+Hospital+Chennai"}
    ],
    "bangalore": [
        {"name": "Fortis Hospital", "location": "Bangalore", "google_maps": "https://www.google.com/maps/search/?api=1&query=Fortis+Hospital+Bangalore"},
        {"name": "Manipal Hospital", "location": "Bangalore", "google_maps": "https://www.google.com/maps/search/?api=1&query=Manipal+Hospital+Bangalore"},
        {"name": "Apollo Hospital", "location": "Bangalore", "google_maps": "https://www.google.com/maps/search/?api=1&query=Apollo+Hospital+Bangalore"}
    ],
    "mumbai": [
        {"name": "Lilavati Hospital", "location": "Mumbai", "google_maps": "https://www.google.com/maps/search/?api=1&query=Lilavati+Hospital+Mumbai"},
        {"name": "Nanavati Hospital", "location": "Mumbai", "google_maps": "https://www.google.com/maps/search/?api=1&query=Nanavati+Hospital+Mumbai"},
        {"name": "Hinduja Hospital", "location": "Mumbai", "google_maps": "https://www.google.com/maps/search/?api=1&query=Hinduja+Hospital+Mumbai"}
    ],
    "delhi": [
        {"name": "AIIMS Hospital", "location": "Delhi", "google_maps": "https://www.google.com/maps/search/?api=1&query=AIIMS+Hospital+Delhi"},
        {"name": "Max Hospital", "location": "Delhi", "google_maps": "https://www.google.com/maps/search/?api=1&query=Max+Hospital+Delhi"},
        {"name": "Fortis Escorts Hospital", "location": "Delhi", "google_maps": "https://www.google.com/maps/search/?api=1&query=Fortis+Escorts+Hospital+Delhi"}
    ],
    "kanchipuram": [
        {"name": "Meenakshi Hospital", "location": "Kanchipuram", "google_maps": "https://www.google.com/maps/search/?api=1&query=Meenakshi+Hospital+Kanchipuram"},
        {"name": "Annai Arul Hospital", "location": "Kanchipuram", "google_maps": "https://www.google.com/maps/search/?api=1&query=Annai+Arul+Hospital+Kanchipuram"},
        {"name": "Govt Hospital", "location": "Kanchipuram", "google_maps": "https://www.google.com/maps/search/?api=1&query=Government+Hospital+Kanchipuram"}
    ],
    "hyderabad": [
        {"name": "Care Hospital", "location": "Hyderabad", "google_maps": "https://www.google.com/maps/search/?api=1&query=Care+Hospital+Hyderabad"},
        {"name": "Yashoda Hospital", "location": "Hyderabad", "google_maps": "https://www.google.com/maps/search/?api=1&query=Yashoda+Hospital+Hyderabad"},
        {"name": "Apollo Hospital", "location": "Hyderabad", "google_maps": "https://www.google.com/maps/search/?api=1&query=Apollo+Hospital+Hyderabad"}
    ]
}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/get_advice', methods=['POST'])
def get_advice():
    try:
        data = request.get_json(force=True)
        symptoms = data.get('symptoms', '').strip()
        location = data.get('location', '').lower()

        if not symptoms:
            return jsonify({"error": "Symptoms not provided."}), 400

        # Prompt for Gemini
        prompt = f"""
        You are a very detailed, kind AI Healthcare Assistant specializing for elderly patients.

        The user is experiencing the following symptoms: {symptoms}

        Please provide a very detailed, nicely formatted healthcare advice that includes:

        🩺Diagnosis:
        - A short paragraph (3-4 lines) about what could be happening.

        💊Recommendations:
        - 3 to 5 bullet points listing advice/tips in simple English.

        Important Warning:
        - If any critical action is needed (like seeing a doctor immediately), mention it clearly.

        🧘 Lifestyle Tips:
        - 2-3 bullet points suggesting lifestyle changes (like drinking water, rest, etc.).

        ✨Tone:
        - Be polite, supportive, motivating, and caring.
        - Make it easy for an older person to understand.

        Format it clearly with emojis, bullet points, and spacing between sections.
        """

        # Generate content
        response = model.generate_content(prompt)
        advice = response.parts[0].text.strip()

        # Formatting
        formatted_advice = advice.replace("🩺", "\n\n🩺 Diagnosis:\n-")
        formatted_advice = formatted_advice.replace("💊", "\n\n💊 Recommendations:\n-")
        formatted_advice = formatted_advice.replace("⚠️", "\n\n⚠️ Important Warning:\n-")
        formatted_advice = formatted_advice.replace("🧘", "\n\n🧘 Lifestyle Tips:\n-")
        formatted_advice = formatted_advice.replace("✨", "\n\n✨ Tone:\n-")
        formatted_advice = formatted_advice.replace("\n\n-", "\n -")

        # Hospital lookup
        hospitals = location_to_hospitals.get(location, [])

        return jsonify({
            "advice": formatted_advice,
            "hospitals": hospitals
        })

    except Exception as e:
        traceback.print_exc()
        return jsonify({"error": "⚠️ Error: An error occurred while generating advice."}), 500

if __name__ == '__main__':
    app.run(debug=True)
