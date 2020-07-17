#include <Servo.h>
Servo myservo; 

//------------------------------------------------- init variables --------------------------

//bat swings in z-direction if k=1
 int k=0;

 //pin numbers for motor forward and backward actuation (x-axis movement)
int motorf=13;
int motorb=12;

// Delay variable
float x;

//Threshold value of radius. Bat hits ball when ball radius is more than rthresh (ball is incoming)
float rthresh=50.0;

 //For data transmission from Python (cvi) to Arduino Serial Monitor
const byte numChars = 32;
char receivedChars[numChars];
char tempChars[numChars];        // temporary array for use when parsing

// variables to hold the parsed data
char messageFromPC[numChars] = {0};
float X_Coordinate = 0.0;
float Radius = 0.0;

//Process handling
boolean newData = false;
int i=0;


//-------------------------------------------------------------------------- void setup() -------------------------
void setup() {

    Serial.begin(9600);
    Serial.println("This demo expects 3 pieces of data - text, an integer and a floating point value");
    Serial.println("Enter data in this style <HelloWorld, 12, 24.7>  ");
    Serial.println();
      myservo.attach(9);  
      pinMode(motorb,OUTPUT);
      pinMode(motorf,OUTPUT);
}

//------------------------------------------------------------------------ void loop() ------------------
void loop() {
    recvWithStartEndMarkers();
    if (newData == true) {
        strcpy(tempChars, receivedChars);
            // this temporary copy is necessary to protect the original data
            //   because strtok() used in parseData() replaces the commas with \0
        parseData();

      
      //------------------------Verfiying results on serial monitor 
    Serial.print("Message ");
    Serial.println(messageFromPC); //test
    Serial.print("Float ");
    Serial.println(X_Coordinate); // X coordinate
    Serial.print("Float ");
    Serial.println(Radius); // radius
    Serial.print("Float ");
    //Variable to switch motor forward and backward movement
    int j=0;

    //Move and hit the ball:
    
    if(i==0){
      x=X_Coordinate;
    digitalWrite(motorf,HIGH);
    delay(5*x);
    digitalWrite(motorf,LOW);
    i=1;
    }
    
    if( Radius > rthresh){
     hit();    
    j =1;
    k=1;
     }

if (j==1){
  digitalWrite(motorb,HIGH);
    delay(5*x);
    digitalWrite(motorb,LOW);
}
        newData = false;
    }  
}


//-----------------------------Functions---

void hit(){
  int pos=135;
   for (pos = 135; pos >= 0; pos -= 1) { // goes from 135 degrees to 0 degrees
    myservo.write(pos);              // tell servo to go to position in variable 'pos'
    delay(5);                       
  }
   for (pos = 0; pos <= 135; pos += 1) { // goes from 0 degrees to 135 degrees
    // in steps of 1 degree
    myservo.write(pos);              
    delay(5);                       
  }
}

void recvWithStartEndMarkers() {
    static boolean recvInProgress = false;
    static byte ndx = 0;
    char startMarker = '<';
    char endMarker = '>';
    char rc;

    while (Serial.available() > 0 && newData == false) {
        rc = Serial.read();

        if (recvInProgress == true) {
            if (rc != endMarker) {
                receivedChars[ndx] = rc;
                ndx++;
                if (ndx >= numChars) {
                    ndx = numChars - 1;
                }
            }
            else {
                receivedChars[ndx] = '\0'; // terminate the string
                recvInProgress = false;
                ndx = 0;
                newData = true;
            }
        }

        else if (rc == startMarker) {
            recvInProgress = true;
        }
    }
}



//------------------------------------------------------- PARSE DATA
void parseData() {      // split the data into its parts

    char * strtokIndx; // this is used by strtok() as an index
    strtokIndx = strtok(tempChars,",");      // get the first part - the string
    strcpy(messageFromPC, strtokIndx); // copy it to messageFromPC
    strtokIndx = strtok(NULL, ","); // this continues where the previous call left off
    X_Coordinate = atof(strtokIndx);     // convert this part to an integer
    strtokIndx = strtok(NULL, ",");
    Radius = atof(strtokIndx); 
    strtokIndx = strtok(NULL, ",");
    velocity = atof(strtokIndx);  // convert this part to a float
}
