import random
import asyncio
import threading
from flask import Flask, render_template
from flask_socketio import SocketIO
from bleak import BleakClient
app=Flask(__name__)
socketio = SocketIO(app)

@app.route('/')
def bluetooth_index():
    return render_template('bluetooth_index.html')

# Replace with your sensor's Bluetooth address and characteristic UUID
BLE_ADDRESS = "XX:XX:XX:XX:XX:XX"  # Sensor's MAC address
CHARACTERISTIC_UUID = "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"  # UUID for reading data

async def read_sensor_data():
    async with BleakClient(BLE_ADDRESS) as client:
        while True:
            data = await client.read_gatt_char(CHARACTERISTIC_UUID)
            # Process the data (e.g., convert from bytes)
            processed_data = int.from_bytes(data, byteorder='little')
            print(f"Sensor Data: {processed_data}")
            # Emit to Socket.IO here (or return data to Flask)
            socketio.emit('sensor_update', {'data': processed_data})
            await asyncio.sleep(1)  # Adjust the interval as needed
            
# Run the BLE connection and reading in the background
# loop = asyncio.get_event_loop()
# loop.run_until_complete(read_sensor_data())
async def simulate_sensor_data():
    """Simulate real-time sensor data and emit to front-end."""
    while True:
        # Simulate sensor data (e.g., random integer between 0 and 100)
        sensor_data = random.randint(0, 100)
        print(f"Simulated Sensor Data: {sensor_data}")
        # Emit sensor data to front-end via Socket.IO
        socketio.emit('sensor_update', {'data': sensor_data})
        await asyncio.sleep(1)  # Send data every second

def background_thread():
    """Start the asyncio loop in a background thread."""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(simulate_sensor_data())

@socketio.on('connect')
def handle_connect():
    """Handle client connection to ensure data streaming starts."""
    global thread
    if not thread.is_alive():
        thread = threading.Thread(target=background_thread)
        thread.start()

if __name__ == '__main__':
    # Start the background thread that will handle sensor data
    thread = threading.Thread(target=background_thread)
    thread.start()
    # Run the Flask application
    socketio.run(app)