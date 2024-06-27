import time
from pymata4 import pymata4

class Keypad:
    rows = [18,19,20,21]
    cols = [14,15,16,17]

    # rows = [5,4,3,2]
    # cols = [9,8,7,6]

    keypad_layout = [
    ['1', '2', '3', 'A'],
    ['4', '5', '6', 'B'],
    ['7', '8', '9', 'C'],
    ['*', '0', '#', 'D']
]
    correct_code = ['3', '3', '9']
    finish_code = ['D', 'D', 'D']
    
    def __init__(self, board) -> None:
        self.board = board
        for row in Keypad.rows:
            self.board.set_pin_mode_digital_output(row)
            self.board.digital_write(row,1)
        for col in Keypad.cols:
            self.board.set_pin_mode_digital_input_pullup(col) 


    @staticmethod
    def get_key(row_pin, col_pin):
        row_index = Keypad.rows.index(row_pin)
        col_index = Keypad.cols.index(col_pin)
        return Keypad.keypad_layout[row_index][col_index]
    
    def debounce_read(self, col):
        self.board.digital_write(col, 0)
        time.sleep(0.05)  # Increased debounce time
        read = self.board.digital_read(col)[0]
        self.board.digital_write(col, 1)
        return read == 0
    
    def scan_keypad(self):
        key_pressed = None
        for row in Keypad.rows:
            self.board.digital_write(row, 0)  # Activate row
            time.sleep(0.01)  # Allow row activation to settle
            for col in Keypad.cols:
                if self.debounce_read(col):  # Check if button is pressed
                    key_pressed = Keypad.get_key(row, col)
                    while self.debounce_read(col):  # Wait for key release with debounce
                        time.sleep(0.01)
                    return key_pressed  # Return immediately after a keypress is detected
            self.board.digital_write(row, 1)  # Deactivate row
        return key_pressed
    
    def run(self):
        print("Starting digicode system. Please wait...")
        time.sleep(2) 
        print("Ready for code entry.")
        entered_code = []
        last_key_time = time.time()
        
        while True:
            key = self.scan_keypad()
            if key:
                current_time = time.time()
                if current_time - last_key_time > 5:
                    entered_code = []  # Reset if too long between presses
                    print("Resetting due to timeout...")
                last_key_time = current_time
                print(f"Key Pressed: {key}")
                entered_code.append(key)

            if len(entered_code) == 3:
                if entered_code == Keypad.correct_code:
                    print("Code Correct. Access Granted.")
                    for _ in range(5):  # Display access signal
                            print(".", end=" ", flush=True)
                            time.sleep(1)
                    print("\nResetting for new code...")
                    entered_code = []
                elif entered_code == Keypad.finish_code:
                        print("Stop")
                        time.sleep(1)
                        break
                else:
                        print("Incorrect Code. Try again.")
                        entered_code = []
        self.board.shutdown()


if __name__ == "__main__":
    board =  pymata4.Pymata4()
    key = Keypad(board)
    key.run()