import sys
import atexit
from PyQt5.QtWidgets import QApplication, QMainWindow, QLineEdit, QLabel, QPushButton
from PyQt5.QtGui import QFont
from PyQt5 import QtCore
from time import sleep
import RPi.GPIO as GPIO
from enum import IntEnum
import threading


# Static variables
sel        = True  # Selects red (True) or green (False) LED
active     = False # Whether a current message is being displayed
UNIT_TIME  = 0.3   # Seconds
MORSE_DICT = {     # Maps characters to morse code
    'a': ".-",
    'b': "-...",
    'c': "-.-.",
    'd': "-..",
    'e': ".",
    'f': "..-.",
    'g': "--.",
    'h': "....",
    'i': "..",
    'j': ".---",
    'k': "-.-",
    'l': ".-..",
    'm': "--",
    'n': "-.",
    'o': "---",
    'p': ".--.",
    'q': "--.-",
    'r': ".-.",
    's': "...",
    't': "-",
    'u': "..-",
    'v': "...-",
    'w': ".--",
    'x': "-..-",
    'y': "-.--",
    'z': "--..",
    '0': "-----",
    '1': ".----",
    '2': "..---",
    '3': "...--",
    '4': "....-",
    '5': ".....",
    '6': "-....",
    '7': "--...",
    '8': "---..",
    '9': "----."
}


class Pin(IntEnum): # GPIOs wired to the LEDs
    RED = 11
    GREEN = 13
    BLUE = 15


def blinkWord(word):
    """
    Blinks a word in morse code

    Parameters
    ----------
    word : str
        the word to blink
    """

    for letter in word:
        blinkLetter(letter)

    # Flag that a new thread can be started
    global active
    active = False


def blinkLetter(letter):
    """
    Blinks a letter from a word as morse code

    Parameters
    ----------
    letter : str
        the character to blink
    """

    # Blink a different LED for an invalid letter
    try:
        code = MORSE_DICT[letter]
    except:
        blink(Pin.BLUE, UNIT_TIME)
        return

    # Blink the letter
    global sel
    blinkCode(Pin.RED if sel else Pin.GREEN, code)
    sel = not sel

    # Delay at the end of a character (3 units - 1 for the end of a code piece)
    sleep(2 * UNIT_TIME)


def blinkCode(led, code):
    """
    Blinks a sequence of morse code symbols

    Parameters
    ----------
    led : int
        the led to blink
    code : str
        the sequence of dashes and dots
    """

    for c in code:
        # Blink longer for a dash
        multi = 1 if c == '.' else 3
        blink(led, multi * UNIT_TIME)


def blink(led, duration):
    """
    Blinks an LED for a set duration

    Parameters
    ----------
    led : int
        the LED to blink
    duration : float
        the length of the blink
    """

    # Turn on
    GPIO.output(led, GPIO.HIGH)
    sleep(duration)

    # Turn off
    GPIO.output(led, GPIO.LOW)
    sleep(duration)


class MyWindow(QMainWindow):
    """
    A class to represent a window GUI
    """

    def __init__(self):
        """
        Constructs a new window
        """

        super().__init__()
        self.setGeometry(50, 50, 640, 480)
        self.setWindowTitle("Morse Code Machine")
        self.initUI()

    def clicked(self):
        """
        Executes more code after a click event
        """

        global active
        if not active:
            # Maintain GUI interactivity with a new thread
            active = True
            thread = threading.Thread(target=blinkWord, args=(self.lineEdit.text().lower(),))
            thread.start()


    def initUI(self):
        """
        Creates all the UI elements in the GUI
        """

        # Label
        self.label = QLabel("Morse Code Machine", self)
        self.label.setFont(QFont('Arial', 24))
        self.label.setFixedSize(340, 30)
        self.label.move(150, 110)
        self.label.setAlignment(QtCore.Qt.AlignCenter)

        # Line edit
        self.lineEdit = QLineEdit("", self)
        self.lineEdit.setPlaceholderText("Enter a word")
        self.lineEdit.setFixedSize(240, 50)
        self.lineEdit.move(200, 190)
        self.lineEdit.setMaxLength(12)
        self.lineEdit.setAlignment(QtCore.Qt.AlignCenter)

        # Button
        self.pushButton = QPushButton(self)
        self.pushButton.setFixedSize(160, 40)
        self.pushButton.move(240, 250)
        self.pushButton.setText("Display")
        self.pushButton.setFocusPolicy(QtCore.Qt.ClickFocus)
        self.pushButton.clicked.connect(self.clicked)


if __name__ == "__main__":

    # Register GPIO cleanup on exit
    atexit.register(GPIO.cleanup)

    # Setup GPIO
    GPIO.setmode(GPIO.BOARD)
    GPIO.setup(Pin.RED, GPIO.OUT)
    GPIO.setup(Pin.GREEN, GPIO.OUT)
    GPIO.setup(Pin.BLUE, GPIO.OUT)

    # Setup GUI
    app = QApplication(sys.argv)
    window = MyWindow()
    window.show()

    # Close program when GUI closes
    sys.exit(app.exec_())