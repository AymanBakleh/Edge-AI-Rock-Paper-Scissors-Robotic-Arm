import leap
import time
import numpy as np
from edge_impulse_linux.runner import ImpulseRunner
from leap.enums import HandType
from leapc_cffi import ffi
from leap.events import TrackingEvent
from leap.event_listener import LatestEventListener
from leap.datatypes import FrameData
import numpy as np
import serial
def wait_until(condition_func, timeout=10):
    start_time = time.time()
    while not condition_func():
        if time.time() - start_time >= timeout:
            raise TimeoutError("Timed out while waiting for condition to be met")
        time.sleep(0.1)
# Define the serial port and baud rate for communication with Arduino
SERIAL_PORT = '/dev/ttyUSB0'  # Change this to match your Arduino's serial port
BAUD_RATE = 9600

# Establish serial connection with Arduino
ser = serial.Serial(SERIAL_PORT, BAUD_RATE)

# Define the gesture mappings
GESTURE_ROCK = "ROCK"
GESTURE_PAPER = "PAPER"
GESTURE_SCISSORS = "SCISSORS"

# Define the gestures recognized by the model
GESTURES = {
    0: GESTURE_ROCK,
    1: GESTURE_PAPER,
    2: GESTURE_SCISSORS
}

# Define the number of fingers
NUM_FINGERS = 5
# Define the total number of features required
TOTAL_FEATURES = 575

# Function to preprocess the hand data for inference
def preprocess_hand_data(hand_data):
    return hand_data

# Modify the listener class to use the preprocess function
class MyListener(leap.Listener):
    def __init__(self, model_runner):
        super().__init__()
        self.model_runner = model_runner

    def on_tracking_event(self, event):
        for hand in event.hands:
            hand_data = extract_hand_info(hand)
            preprocessed_data = preprocess_hand_data(hand_data)
            try:
                result = self.model_runner.classify(preprocessed_data)
                gesture_index = np.argmax(result['classification'])
                gesture = GESTURES[gesture_index]
                print("Inference result:", gesture)
                send_gesture_to_arduino(gesture)
            except Exception as e:
                print("ERROR: Could not perform inference")
                print("Exception:", e)

# Modify the extract_hand_info function to extract finger data
def extract_hand_info(hand):
    # Extract finger data (whether each finger is extended or not)
    hand_data = [int(digit.is_extended) for digit in hand.digits]
    return hand_data

# Function to send gesture commands to Arduino
def send_gesture_to_arduino(gesture):
    command = "GESTURE " + gesture + "\n"
    ser.write(command.encode())

def main():
    model_file = "/home/ayman/Desktop/data/modelfile.eim"  # Path to your model file
    model_runner = ImpulseRunner(model_file)
    try:
        model_info = model_runner.init()
        print("Model name:", model_info['project']['name'])
        print("Model owner:", model_info['project']['owner'])
    except Exception as e:
        print("ERROR: Could not initialize model")
        print("Exception:", e)
        exit()

    tracking_listening = LatestEventListener(leap.EventType.Tracking)
    connection = leap.Connection()
    connection.add_listener(tracking_listening)

    with connection.open() as open_connection:
        wait_until(lambda: tracking_listening.event is not None)
        listener = MyListener(model_runner)
        connection.add_listener(listener)

        # Ctrl-C to exit
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("Inference stopped.")

if __name__ == "__main__":
    main()
