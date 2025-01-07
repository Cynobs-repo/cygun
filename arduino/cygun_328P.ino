unsigned long serialSpeed = 9600;
unsigned long debounceDelay = 10;    // the debounce time; increase if the output flickers
String arduIDname = "Lightgun_Arduino_1";

// constants won't change. They're used here to set pin numbers:
const int buttonPin0 = 2;  // the number of the pushbutton pin
const int buttonPin1 = 3;
const int buttonPin2 = 4;
const int buttonPin3 = 5;
const int buttonPin4 = 6;

// Variables will change:
int ledState = HIGH;        // the current state of the output pin
int buttonState0;            // the current reading from the input pin
int buttonState1; 
int buttonState2; 
int buttonState3; 
int buttonState4; 
int lastButtonState0 = LOW;  // the previous reading from the input pin
int lastButtonState1 = LOW;
int lastButtonState2 = LOW;
int lastButtonState3 = LOW;
int lastButtonState4 = LOW;

// the following variables are unsigned longs because the time, measured in
// milliseconds, will quickly become a bigger number than can be stored in an int.
unsigned long lastDebounceTime0 = 0;  // the last time the output pin was toggled
unsigned long lastDebounceTime1 = 0; 
unsigned long lastDebounceTime2 = 0; 
unsigned long lastDebounceTime3 = 0; 
unsigned long lastDebounceTime4 = 0; 


String inputString = "";      // a String to hold incoming data
String getidcommand = "get ID";  // Vorgabesatz

void setup() {
  Serial.begin(serialSpeed);
  
  pinMode(buttonPin0, INPUT_PULLUP);
  pinMode(buttonPin1, INPUT_PULLUP);
  pinMode(buttonPin2, INPUT_PULLUP);
  pinMode(buttonPin3, INPUT_PULLUP);
  pinMode(buttonPin4, INPUT_PULLUP);

}

void loop() {
  // read the state of the switch into a local variable:
  int reading0 = digitalRead(buttonPin0);
  int reading1 = digitalRead(buttonPin1);
  int reading2 = digitalRead(buttonPin2);
  int reading3 = digitalRead(buttonPin3);
  int reading4 = digitalRead(buttonPin4);

  // If the switch changed, due to noise or pressing:
  if (reading0 != lastButtonState0) {
    // reset the debouncing timer
    lastDebounceTime0 = millis();
  }
  if (reading1 != lastButtonState1) {
    // reset the debouncing timer
    lastDebounceTime1 = millis();
  }
  if (reading2 != lastButtonState2) {
    // reset the debouncing timer
    lastDebounceTime2 = millis();
  }
  if (reading3 != lastButtonState3) {
    // reset the debouncing timer
    lastDebounceTime3 = millis();
  }
  if (reading4 != lastButtonState4) {
    // reset the debouncing timer
    lastDebounceTime4 = millis();
  }

  char buttonpressed[] = "00000";
  int length = sizeof(buttonpressed) / sizeof(buttonpressed[0]);

  if ((millis() - lastDebounceTime0) > debounceDelay) {
    if (reading0 != buttonState0) {
      buttonState0 = reading0;
      if (buttonState0 == HIGH) {
        buttonpressed[0] = 'R';
      } else {
        buttonpressed[0] = 'P';
      }
    }
  }

  if ((millis() - lastDebounceTime1) > debounceDelay) {
    if (reading1 != buttonState1) {
      buttonState1 = reading1;
      if (buttonState1 == HIGH) {
        buttonpressed[1] = 'R';
      } else {
        buttonpressed[1] = 'P';
      }
    }
  }

    if ((millis() - lastDebounceTime2) > debounceDelay) {
    if (reading2 != buttonState2) {
      buttonState2 = reading2;
      if (buttonState2 == HIGH) {
        buttonpressed[2] = 'R';
      } else {
        buttonpressed[2] = 'P';
      }
    }
  }

    if ((millis() - lastDebounceTime3) > debounceDelay) {
    if (reading3 != buttonState3) {
      buttonState3 = reading3;
      if (buttonState3 == HIGH) {
        buttonpressed[3] = 'R';
      } else {
        buttonpressed[3] = 'P';
      }
    }
  }

    if ((millis() - lastDebounceTime4) > debounceDelay) {
    if (reading4 != buttonState4) {
      buttonState4 = reading4;
      if (buttonState4 == HIGH) {
        buttonpressed[4] = 'R';
      } else {
        buttonpressed[4] = 'P';
      }
    }
  }

  // save the reading. Next time through the loop, it'll be the lastButtonState:
  lastButtonState0 = reading0;
  lastButtonState1 = reading1;
  lastButtonState2 = reading2;
  lastButtonState3 = reading3;
  lastButtonState4 = reading4;

  // If there is a state change > report it
  if (!strcmp(buttonpressed, "00000") == 0) {
    Serial.println(buttonpressed);
  }

  if (Serial.available() > 0) {  // Prüfen, ob Daten empfangen wurden
    char zeichen = Serial.read();  // Einzelnes Zeichen einlesen
    if (zeichen == '\n') {  // Prüfen, ob die Eingabe abgeschlossen ist
      if (inputString.equals(getidcommand)) {  // Eingabe mit Vorgabe vergleichen
        Serial.println(arduIDname);  // Antwort senden
      }
      inputString = "";  // Eingabe zurücksetzen
    } else {
      inputString += zeichen;  // Zeichen zur Eingabe hinzufügen
    }
  }
}

