# Agro Rishi

**Agro Rishi** is a comprehensive web application designed to empower farmers with cutting-edge technology, offering solutions for real-time sensor tracking, native language interaction, community engagement, and crop disease detection. Built using Flask, this application integrates multiple features to provide a seamless and efficient user experience.

## Features

### 1. Real-Time Sensor Tracking
Agro Rishi enables real-time monitoring of agricultural sensors using `socket.io` and threading techniques. Farmers can connect their Bluetooth devices and fetch data from nearby sensors to track environmental conditions on their farms. 

### 2. Native Language Chatbot
Our chatbot uses **Llama3 LLM** and **pyttsx3** for natural language processing and text-to-speech functionalities. The chatbot currently operates independently but is being integrated into the main application to provide a unified user interface. This feature aims to support native languages for better accessibility and interaction.

### 3. Agro Community
The Agro Community is a public forum where farmers can post about their crops, share experiences, and receive upvotes from the community. These upvotes will contribute to a preference algorithm, helping highlight the most relevant posts. This feature is still under development.

### 4. Crop Disease Detection
Agro Rishi includes a feature for detecting crop diseases using image classification models. This feature is currently under construction, with the goal of providing farmers with instant feedback on the health of their crops.

## Screenshots
Real time Sensor tracking(Using sample database)
 ![WhatsApp Image 2024-08-10 at 17 08 52_fec3d2e6](https://github.com/user-attachments/assets/4f1af2f8-09a7-405b-ae6f-85ae4a1af1be)
![WhatsApp Image 2024-08-10 at 17 10 05_bad98a2f](https://github.com/user-attachments/assets/f0b891dc-bdd1-42d8-b6a8-cc7776bb40cf)

Asssitant using llama model
![Screenshot 2024-08-10 171547](https://github.com/user-attachments/assets/dbb38df9-eef9-4c80-badd-c3f11719e251)
![Screenshot 2024-08-10 171728](https://github.com/user-attachments/assets/db816fbc-e4e3-45d7-b2a7-2b6d749fd1ad)


## Installation
For installation, you need a llm model locally,
Download [https://ollama.com/]  then
```bash
    ollama run llama3
```

To run Agro Rishi locally, follow these steps:

1. Clone the repository:
    ```bash
    git clone https://github.com/your-username/agro-rishi.git
    cd agro-rishi
    ```

2. Create a virtual environment:
    ```bash
    python3 -m venv venv
    source venv/bin/activate
    ```

3. Install the dependencies:
    ```bash
    pip install -r requirements.txt
    ```

4. Run the Flask application:
    ```bash
    flask run
    ```

5. Access the application at `http://127.0.0.1:5000/`.


