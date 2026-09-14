import os
import leap
import time
import csv
import numpy as np
from leapc_cffi import ffi
from leap.events import TrackingEvent
from leap.event_listener import LatestEventListener
from leap.datatypes import FrameData

class FrameData:
    def __init__(self, size):
        self._buffer = ffi.new("char[]", size)
        self._frame_ptr = ffi.cast("LEAP_TRACKING_EVENT*", self._buffer)

    def __getattr__(self, name):
        if name == "tracking_frame_id":
            return self._frame_ptr.tracking_frame_id
        elif name == "info":
            return self._frame_ptr.info
        elif name == "nHands":
            return self._frame_ptr.nHands
        elif name == "framerate":
            return self._frame_ptr.framerate
        elif name == "pHands":
            return self._frame_ptr.pHands
        raise AttributeError(f"'FrameData' object has no attribute '{name}'")

    def frame_ptr(self):
        return self._frame_ptr

    def get_palm(self, hand):
        return hand.palm

    def get_hands(self):
        hands = []
        for i in range(self._frame_ptr.nHands):
            hand_ptr = ffi.cast("LEAP_HAND*", self._frame_ptr.pHands[i])
            hands.append(hand_ptr[0])
        return hands

    def get_arm(self, hand):
        return hand.arm

def wait_until(condition_func, timeout=10):
    start_time = time.time()
    while not condition_func():
        if time.time() - start_time >= timeout:
            raise TimeoutError("Timed out while waiting for condition to be met")
        time.sleep(0.1)

class MyListener(leap.Listener):
    def __init__(self):
        super().__init__()
        self.sample_count = 0

    def on_connection_event(self, event):
        print("Connected")

    def on_device_event(self, event):
        try:
            with event.device.open():
                info = event.device.get_info()
        except leap.LeapCannotOpenDeviceError:
            info = event.device.get_info()

        print(f"Found device {info.serial}")

    def on_tracking_event(self, event):
        for hand in event.hands:
            hand_data = extract_hand_info(hand)

            # Add timestamp to hand data
            timestamp = int(time.time())
            hand_data.append(timestamp)

            # Save the data to a CSV file in the corresponding label folder
            self.sample_count += 1
            csv_filename = os.path.join(label, f"sample_{self.sample_count}.csv")
            with open(csv_filename, 'w', newline='') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(header)  # Write the header
                writer.writerow(hand_data)
            print(f"Saved sample {self.sample_count} to {csv_filename}")

def extract_vector_info(vector):
    return [int(vector.x), int(vector.y), int(vector.z)]

def extract_palm_info(palm):
    return extract_vector_info(palm.position)

def extract_digit_info(digit):
    return [int(digit.is_extended)]

def extract_hand_info(hand):
    hand_data = [
        hand.id,
        hand.flags,
        1 if hand.type == leap.HandType.Left else 0,  # Convert HandType to integer
    ]
    hand_data.extend(extract_palm_info(hand.palm))
    for digit in hand.digits:
        hand_data.extend(extract_digit_info(digit))
    return hand_data

def preprocess_hand_data(hand_data):
    hand_data = np.array(hand_data, dtype=np.int32)  # Ensure all data is converted to int
    return hand_data.tolist()

def generate_header():
    header = [
        "hand_id", "hand_flags", "hand_type",
        "palm_position_x", "palm_position_y", "palm_position_z",
    ]
    for finger_id in range(5):
        header.append(f"finger_{finger_id}_is_extended")
    header.append("timestamp")  # Add timestamp to header
    return header
def main():
    global label
    label = input("Enter the label for this data collection session: ")

    # Ensure label directory exists
    os.makedirs(label, exist_ok=True)

    global header
    header = generate_header()

    tracking_listening = LatestEventListener(leap.EventType.Tracking)

    connection = leap.Connection()
    connection.add_listener(tracking_listening)

    with connection.open() as open_connection:
        wait_until(lambda: tracking_listening.event is not None)
        listener = MyListener()
        connection.add_listener(listener)

        # Ctrl-C to exit
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("Data collection stopped.")

if __name__ == "__main__":
    main()