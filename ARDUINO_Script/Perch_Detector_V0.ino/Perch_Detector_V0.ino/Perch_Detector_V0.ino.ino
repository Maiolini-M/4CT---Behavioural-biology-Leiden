/* ************************************************************************************************************************************************
 *  
 *                                                       ELD2416
 *                                                       Perch Detector V1.0
 *                              
 *                                                       LION/ELD
 *                                                       Peter Numberi
 *                                                       06/06/2024
 *  
 *  
 *   Hardware:
 *   - Arduino Mega 2560    
 *   https://content.arduino.cc/assets/Pinout-Mega2560rev3_latest.png
 *   - Supply 5V External or 5V USB power (default)   
 *   - 4CH relay board 5V control logic/up to 250Vac switching
 *   https://www.tinytronics.nl/en/switches/relays/5v-relay-4-channel-high-active-or-low-active
 *   
 *    
 *   ************    Mega 2560 Pinout   *************
 *   Inputs:
 *   SW1 = 18     ==> needs 10K/100n RC filter for debounce/stability
 *   SW2 = 19     ==> needs 10K/100n RC filter for debounce/stability
 *   SW3 = 20     ==> needs 10K/100n RC filter for debounce/stability
 *   SW4 = 21     ==> needs 10K/100n RC filter for debounce/stability
 *   
 *   Outputs:
 *   RELAY1 = 5
 *   RELAY2 = 4
 *   RELAY3 = 3
 *   RELAY4 = 2
 *   
 *   - SW inputs wired via 4x Lumberg 6P DIN connectors (KV 60), contacs on two centre pins (3 & 6)
 *   https://docs.rs-online.com/f502/0900766b80e0a56e.pdf
 *   - Relay/Speaker outputs wired via RCA connectors (4x)
 *   - Sound source input via RCA connecter labelled "input".
 *   
 *   Software:
 *   - USB/SERIAL settings 115200/8/N/1, use CR/NL as terminator when sending data to (Arduino) controller   
 *   
 *   **************  Serial command set ****************************
 *   
 *
 *
 *       **** Single char commands ****"  
 *        - h ==> Help/get command info");  
 *        - n ==> Run mode  (disables actor action)");  
 *        - p ==> Stop mode (enables actor action )");  
 *        - c ==> Clear Arduino controller settings (revert to default values) and reset");  
 *        - r ==> Reset controller, this restarts Arduino but keeps settings");                             
 *                                     
 *        **** SETTERS ****");  
 *        - [sdxxx] ==> Set Delay with xxx as timing in mSecs ==> sd210 = set delay to 120 mSecs");      
 *        - [saxy]  ==> Set audio channel, where [x] is channel (1-4) and [y] is open/close with 0=open and 1=cose.");  
 *        - l ==> list current state with thse parameters:
          1: RUNMODE ==> 0=OFF, 1 = ON
          2: Switch Debounce delay (in mSecs)    
          3: State SW1 ==> 0=OFF, 1 = ON
          4: State SW2 ==> 0=OFF, 1 = ON
          5: State SW3 ==> 0=OFF, 1 = ON
          6: State SW4 ==> 0=OFF, 1 = ON
          
          7: State Relay 1 ==> 0=OFF, 1 = ON 
          8: State Relay 2 ==> 0=OFF, 1 = ON    
          9: State Relay 3 ==> 0=OFF, 1 = ON     
          10: State Relay 4 ==> 0=OFF, 1 = ON           
 *                                     
 *        **** GETTERS ****");  
 *        - [gcx] ==> Get count x ==> gc3 = get count perch 3");             
 *   
 *   
 *   
 *   
 *  
 *  
 *  ***********************************************************************************************************************************************
 */
#include <EEPROM.h>                         // eeprom lib,  used to store variables in non volatile memory (NVM)

#define TPD_PIN  12         // pin 52

#define NVM_CHK_ADR      2  // NVM address perch count
#define NVM_CH1_CNT_ADR  4  // NVM address perch count
#define NVM_CH2_CNT_ADR  6  // NV // NVM address perch count
#define NVM_CH3_CNT_ADR  8  // NV // NVM address perch count
#define NVM_CH4_CNT_ADR  10 // NVM address perch count
#define NVM_ACT_DLY_ADR  12 // NVM actor delay
//#define NVM_CHECKVAL     2

// Debug output switch
const int DBG_MODE        = 0;        // 0=OFF, 1=PRINT OUT, 2=PLOTTER
const bool SHW_LATENCY    = 0;        // 0=OFF, 1=ON 
const int POLL_MODE       = 0;        // Poll or event mode;  0 = poll off & event on, 1 = poll on & event off

const int PERCH_ACC_THR   = 0;
const int UPD_SEN_INTVAL  = 0;        // Sensor interval in mSecs
const int UPD_SOP_INTVAL  = 10;       // Set output interval in mSecs
const int UPD_DBG_INTVAL  = 1000;     // Debug interval in mSecs
const int UPD_PLT_INTVAL  = 40;       // Plotter interval in mSecs

const uint16_t Max_Latency = 5000;    //  Max latency time n mSecs // 2500 mSecs
uint16_t DEBOUNCE_DLY =  125;          // debounce delay

const int Q1_DLY_CNT =  0;        // debounce timer for CH1
const int Q2_DLY_CNT =  0;        // debounce timer for CH2
const int Q3_DLY_CNT =  0;        // debounce timer for CH3
const int Q4_DLY_CNT =  0;        // debounce timer for CH4

volatile int UPD_SEN_CNT = 0;     // Timer/counter for scheduling timing
volatile int UPD_SOP_CNT = 0;     // Timer/counter for scheduling timing
volatile int UPD_DBG_CNT = 0;     // Timer/counter for scheduling timing
volatile int UPD_PLT_CNT = 0;     // Timer/counter for scheduling timing

volatile int LAT1_TMR = 0;        // Latency 1 timer
volatile int LAT2_TMR = 0;        // Latency 2 timer
volatile int LAT3_TMR = 0;        // Latency 3 timer
volatile int LAT4_TMR = 0;        // Latency 4 timer

bool Perch_SW1_State = 0;         // Holds actual switch state
bool Perch_SW2_State = 0;         // Holds actual switch state
bool Perch_SW3_State = 0;         // Holds actual switch state
bool Perch_SW4_State = 0;         // Holds actual switch state

bool Old_SW1_State = 0;           // Required for state change over detection
bool Old_SW2_State = 0;           // Required for state change over detection
bool Old_SW3_State = 0;           // Required for state change over detection
bool Old_SW4_State = 0;           // Required for state change over detection

bool Set_Q1_State = 0;            // Holds set state for relay
bool Set_Q2_State = 0;            // Holds set state for relay
bool Set_Q3_State = 0;            // Holds set state for relay
bool Set_Q4_State = 0;            // Holds set state for relay

bool TPD_STATE = 0;               // Test point debug
int ILED = 13;                    // Internal/PCB LED

int Perch_SW1_PIN = 18;           // Perch microswitch pin CH1
int Perch_SW2_PIN = 19;           // Perch microswitch pin CH2
int Perch_SW3_PIN = 20;           // Perch microswitch pin CH3
int Perch_SW4_PIN = 21;           // Perch microswitch pin CH4

int SPK_Q1_PIN = 5;               // Perch relay pin CH1
int SPK_Q2_PIN = 4;               // Perch relay pin CH2
int SPK_Q3_PIN = 3;               // Perch relay pin CH3
int SPK_Q4_PIN = 2;               // Perch relay pin CH4



// ISR counters
volatile uint16_t MSEC_CNT        = 0;        // mSec counter 

volatile uint16_t Perch_CH1_Count = 0;        // Holds count of perches
volatile uint16_t Perch_CH2_Count = 0;        // Holds count of perches
volatile uint16_t Perch_CH3_Count = 0;        // Holds count of perches
volatile uint16_t Perch_CH4_Count = 0;        // Holds count of perches

// Serial/GUI parser variables
char rx_byte                    = 0;           // used in the serial read routine
String CMD_STR                  = "";          // used in the serial read routine
char CMD_CHAR                   = 0;           // used in the serial read routine
int CMD_byte                    = 0;           // used in the serial read routine
String rx_str                   = "";          // used in the serial read routine
char rx_arr[10];                               // array for storing the serial RXD chars from GUI/PC
int rx_index                    = 0;           // rx pos/index for array 
long SER_RXD_VAL                = 0;           // received RXD value
int GET_VAL                     = 0;           // serial receive value


bool RUNMODE = 0;                               // 0 = STOP , RUN = 1
long Runtime = 0;                               // Runtine in sec after reset/start

int SW1_ACC_TMR = 0;
int SW2_ACC_TMR = 0;
int SW3_ACC_TMR = 0;
int SW4_ACC_TMR = 0;

int NVM_CHECKVAL = 0;

// the setup routine runs once when you press reset:
void setup()
{
  Serial.begin(115200);                       // start serial
  
  while(!Serial);

  if(DBG_MODE != 2 )
  {
    Serial.println("Perch Detector V0 starting...");            // startup serial text    
  }

  // initialize GPIO
  pinMode(ILED, OUTPUT);

  pinMode(TPD_PIN, OUTPUT);
  
  pinMode(SPK_Q1_PIN, OUTPUT);        // Define pin
  pinMode(SPK_Q2_PIN, OUTPUT);        // Define pin
  pinMode(SPK_Q3_PIN, OUTPUT);        // Define pin
  pinMode(SPK_Q4_PIN, OUTPUT);        // Define pin
  
  pinMode(Perch_SW1_PIN, INPUT_PULLUP); // Define pin
  pinMode(Perch_SW2_PIN, INPUT_PULLUP); // Define pin
  pinMode(Perch_SW3_PIN, INPUT_PULLUP); // Define pin
  pinMode(Perch_SW4_PIN, INPUT_PULLUP); // Define pin


  // ***********  setup and initialize timer1 of Arduino Mega for task scheduling timers (via ISR) ******************************************************************
  noInterrupts();                       // disable all interrupts
  TCCR1A = 0;                           // direct register setting
  TCCR1B = 0;                           // direct register setting

  TCNT1 = 65473;                        // preload timer 65473 ==>  65536-16MHz/256/2Hz into register ==> will trigger every 0.2 mSec
  TCCR1B |= (1 << CS12);                // 256 (prescaler) 
  TIMSK1 |= (1 << TOIE1);               // enable timer overflow 
  interrupts();                         // enable all interrupts
 // *************************************************************************************************************************************

  delay(50); // add delay   

   //Defaults(); // testing only

   NVM_CHECKVAL = EEPROM.read(NVM_CHK_ADR);               // Location of NVM_CHECKVAL = 2

   if(NVM_CHECKVAL == 2)                                  // eeprom has been programmed previously get parameters from NVM
   {
     Serial.println("NVM DATA STORED...");              // startup serial text
    
     EEPROM.get(NVM_CH1_CNT_ADR,Perch_CH1_Count);         // Load Perch count from memory   
     EEPROM.get(NVM_CH2_CNT_ADR,Perch_CH2_Count);         // Load Perch count from memory     
     EEPROM.get(NVM_CH3_CNT_ADR,Perch_CH3_Count);         // Load Perch count from memory   
     EEPROM.get(NVM_CH4_CNT_ADR,Perch_CH4_Count);         // Load Perch count from memory   
     EEPROM.get(NVM_ACT_DLY_ADR,DEBOUNCE_DLY);                 // Load Perch count from memory   

     if(DBG_MODE != 2 )
     {
        Serial.println("Fetched NVM data:");            // 
        Serial.print("Perch_CH1_Count: ");              // 
        Serial.println(Perch_CH1_Count);                // 
        Serial.print("Perch_CH2_Count: ");              // 
        Serial.println(Perch_CH2_Count);                // 
        Serial.print("Perch_CH3_Count: ");              // 
        Serial.println(Perch_CH3_Count);                // 
        Serial.print("Perch_CH4_Count: ");              //  
        Serial.println(Perch_CH4_Count);                // 
        Serial.print("Debounce delay: ");               // 
        Serial.println(DEBOUNCE_DLY);                   //          
     }       
   }
   else
   {
     NVM_CHECKVAL = 2;

     Serial.println("NO NVM DATA STORED...");               // startup serial text

     EEPROM.write(NVM_CHK_ADR, NVM_CHECKVAL);               //
     delay(20);
     
     Perch_CH1_Count = 0;                                   // reset count
     Perch_CH2_Count = 0;                                   // reset count
     Perch_CH3_Count = 0;                                   // reset count
     Perch_CH4_Count = 0;                                   // reset count 
     DEBOUNCE_DLY = 125;                                    // default value actor delay   
   
     EEPROM.put(NVM_CH1_CNT_ADR, uint16_t(Perch_CH1_Count));        //
     delay(20);
     EEPROM.put(NVM_CH2_CNT_ADR, uint16_t(Perch_CH2_Count));        //
     delay(20);
     EEPROM.put(NVM_CH3_CNT_ADR, uint16_t(Perch_CH3_Count));        // 
     delay(20);
     EEPROM.put(NVM_CH4_CNT_ADR, uint16_t(Perch_CH4_Count));        //
     delay(20);
     EEPROM.put(NVM_ACT_DLY_ADR, uint16_t(DEBOUNCE_DLY));                //
     delay(20);     
   }

   if(DBG_MODE != 2 )
   {
      Serial.println("Perch Detector init done, starting in stopmode...");            // startup serial text    
   }
  
}

// ***********************************************  resetFunc   *****************************************************************************************************
// resets the Arduino
void(* resetFunc) (void) = 0;                    // declare reset fuction at address 0, this will soft reset the MCU (eeprom NOT erased!)
// ---   end reset function




// **************************************************************************************************************************************************
//                                                                      Defaults
// - 
// - 
// - 
// -
// **************************************************************************************************************************************************
void Defaults()
{
   Perch_CH1_Count = 0;                                   // reset count
   Perch_CH2_Count = 0;                                   // reset count
   Perch_CH3_Count = 0;                                   // reset count
   Perch_CH4_Count = 0;                                   // reset count
   
   DEBOUNCE_DLY = 250;                                         // defult value actor delay   
   
   EEPROM.write(NVM_CHK_ADR, 0);                          // Check ADR value
   delay(20);
   EEPROM.put(NVM_CH1_CNT_ADR, Perch_CH1_Count);          // reset count 
   delay(20);
   EEPROM.put(NVM_CH2_CNT_ADR, Perch_CH2_Count);          // reset count 
   delay(20);
   EEPROM.put(NVM_CH3_CNT_ADR, Perch_CH3_Count);          // reset count 
   delay(20);
   EEPROM.put(NVM_CH4_CNT_ADR, Perch_CH4_Count);          // reset count 
   delay(20);
   EEPROM.put(NVM_ACT_DLY_ADR, uint16_t(DEBOUNCE_DLY));        //
   delay(20);
}


// **************************************************************************************************************************************************
//                                                                      CheckSerial
// - Get input from PC/USB
// - Parse commands for program
// - Returns "*" ==> input OK
// - Returns "x" = input not valid
// **************************************************************************************************************************************************
void CheckSerial()
{
   while(Serial.available())                       // is a character available?
   {    
      rx_byte = Serial.read();                    // get the character
      
          if(rx_byte != '\n')
          {
            // a character of the string was received
            rx_str += rx_byte;
            rx_arr[rx_index] = rx_byte;
            rx_index++;
          }
          else // newline detected, start parsing the string
          {
              //Serial.println();                   // debug only , uncomment for debug
              //Serial.print("GUI CMD: ");          // debug only , uncomment for debug
              //Serial.println(rx_str);             // debug only , uncomment for debug            
            
                    switch(rx_arr[0])
                    {
                       case 'h': //  help/info                         
                            Serial.println("*************************************  SERIAL (PC GUI/USB) COMMAND LIST:  ********************************************************");  
                            Serial.println(" (use 115200/8/N/1 + use [NL+CR] in the packet terminator)");  
                            Serial.println(""); 
                            Serial.println(" **** Single char commands ****");  
                            Serial.println(" - h ==> Help/get command info");  
                            Serial.println(" - n ==> Run mode  (disables actor action)"); 
                            Serial.println(" - l ==> list current state with thse parameters:");
                            Serial.println(" 1: RUNMODE ==> 0=OFF, 1 = ON");
                            Serial.println(" 2: SW Delay: xxx in mSecs");   
                            Serial.println(" 3: State SW1 ==> 0=OFF, 1 = ON");
                            Serial.println(" 4: State SW2 ==> 0=OFF, 1 = ON");
                            Serial.println(" 5: State SW3 ==> 0=OFF, 1 = ON");
                            Serial.println(" 6: State SW4 ==> 0=OFF, 1 = ON");
                            Serial.println(" 7: State Relay 1 ==> 0=OFF, 1 = ON"); 
                            Serial.println(" 8: State Relay 2 ==> 0=OFF, 1 = ON");     
                            Serial.println(" 9: State Relay 3 ==> 0=OFF, 1 = ON");     
                            Serial.println(" 10: State Relay 4 ==> 0=OFF, 1 = ON");                         
                              
                            Serial.println(" - p ==> Stop mode (enables actor action )");  
                            Serial.println(" - c ==> Clear Arduino controller settings (revert to default values) and reset");  
                            Serial.println(" - r ==> Reset controller, this restarts Arduino but keeps settings");                             
                            Serial.println("");                               
                            Serial.println(" **** SETTERS **** ");  
                            Serial.println(" - [sdxxx] ==> Set Delay with xxx as timing in mSecs ==> sd210 = set delay to 120 mSecs");      
                            Serial.println(" - [saxy]  ==> Set audio channel, where [x] is channel (1-4) and [y] is open/close with 0=open and 1=cose.");  
                            Serial.println("");                              
                            Serial.println(" **** GETTERS ****");  
                            Serial.println(" - [gcx] ==> Get count x ==> gc3 = get count perch 3");                                    
                            Serial.println("");   
                       break; 

                       case 'l': // LIST, list parameters                         
                            //Serial.println("*");                                // ACK/CMD OK
                            //Serial.println("LIST");                             // SERIAL/Debug FEEDBACK
                            Serial.println("");                                   // ACK/CMD OK
                            Serial.println(RUNMODE);
                            Serial.println(DEBOUNCE_DLY);
                            Serial.println(Perch_SW1_State);
                            Serial.println(Perch_SW2_State);
                            Serial.println(Perch_SW3_State);
                            Serial.println(Perch_SW4_State);                            
                            Serial.println(Set_Q1_State);
                            Serial.println(Set_Q2_State);
                            Serial.println(Set_Q3_State);
                            Serial.println(Set_Q4_State);
                       break; 
                       
                       
                       case 'n': // run mode, logic and relays enabled
                          if(DBG_MODE != 2 )
                          {
                            Serial.println("*");                                // ACK/CMD OK
                            Serial.println("RUNMODE");                          // SERIAL/Debug FEEDBACK
                          }   
                                                
                          RUNMODE = 1;   
                       break; 

                       case 'p': // stop mode, all relays and action stopped
                          if(DBG_MODE != 2 )
                          {
                            Serial.println("*");                                // ACK/CMD OK
                            Serial.println("STOPMODE");                         // SERIAL/Debug FEEDBACK
                          }
                         
                          RUNMODE = 0;
                       break; 

                       case 'c': // clear, reset with NVM erased and set to factory default
                          if(DBG_MODE != 2 )
                          {
                            Serial.println("*");                               // ACK/CMD OK
                            Serial.println("CLEAR");                        // SERIAL/Ddebug FEEDBACK
                          }
                          
                          Defaults();
                       break; 

                       case 'r': // reset, with NVM no erased
                          if(DBG_MODE != 2 )
                          {
                            Serial.println("*");                              // ACK/CMD OK
                            Serial.println("RESET");                          // SERIAL/Ddebug FEEDBACK
                          }
                         
                          delay(500);                                         // wait before resetting
                          resetFunc();                                        // call MCU reset, this will reboot the Arduino (all RAM storage will be lost).                       break;                      

                       //****************************************   SETTERS     *********************************************************

                       case 's': // setters
                            switch(rx_arr[1])
                            { 
                                  case 'd': // set delay
                                      Serial.println();                                     // spacer
                                      rx_str = rx_str.substring(2);                         // strip off first 2 chars
                                      SER_RXD_VAL = rx_str.toInt();                         // assign newly rxd data to SER_RXD_VAL
                                      GET_VAL = SER_RXD_VAL;                                // assign TOP_SPD with new value
                                      
                                      if((GET_VAL > 0) && (GET_VAL < 1000))                 // max value TBD
                                      {
                                        if(DBG_MODE != 2 )
                                        {
                                           Serial.println("*");                             // reply ACK to GUI
                                        }   

                                        DEBOUNCE_DLY =  GET_VAL;     

                                        EEPROM.put(NVM_ACT_DLY_ADR, DEBOUNCE_DLY);               //
                                        
                                        delay(10);                                           //
                                       
                                      }
                                      else
                                      {
                                        //Serial.println("Entered configuration value out of range, please retry.... ");  // bad entry response
                                        Serial.println("x");  // bad entry response
                                      }
                                  break;   

                                  case 'a': // set audio path 

                                       Serial.println();                      // spacer
                                      //Serial.println("sa OK ");              // reply ACK to GUI                                          
                                      // Serial.println("rx_arr[2]:");          // reply ACK to GUI
                                      //Serial.println(rx_arr[2]);             // reply ACK to GUI

                                      if(SHW_LATENCY)
                                      {
                                           if(LAT1_TMR < Max_Latency)
                                           {
                                           Serial.print("Latency SW1: "); 
                                           Serial.print(LAT1_TMR); 
                                           Serial.println(" mSecs"); 
                                           }
      
                                           if(LAT2_TMR < Max_Latency)
                                           {
                                           Serial.print("Latency SW2: "); 
                                           Serial.print(LAT2_TMR); 
                                           Serial.println(" mSecs"); 
                                           }
      
      
                                           if(LAT3_TMR < Max_Latency)
                                           {
                                             Serial.print("Latency SW3: "); 
                                             Serial.print(LAT3_TMR); 
                                             Serial.println(" mSecs"); 
                                           }
      
                                           if(LAT4_TMR < Max_Latency)
                                           {
                                             Serial.print("Latency SW4: "); 
                                             Serial.print(LAT4_TMR); 
                                             Serial.println(" mSecs"); 
                                           }
                                      }                                     
                                         
                                      switch(rx_arr[2])
                                      {
                                         case '1': // set audio path                                           
                                              rx_str = rx_str.substring(3);                         // strip off first 2 chars
                                              SER_RXD_VAL = rx_str.toInt();                         // assign newly rxd data to SER_RXD_VAL

                                              // Serial.println();                                     // spacer
                                              // Serial.println("rx_str case 1:");                     // reply ACK to GUI
                                              // Serial.println(SER_RXD_VAL);                          // reply ACK to GUI                                              

                                              if(SER_RXD_VAL == 0)
                                              {
                                                  Set_Q1_State = 0;
                                                  //Serial.println("0");                             // reply ACK to GUI  
                                              }

                                              if(SER_RXD_VAL == 1)
                                              {
                                                  Set_Q1_State = 1;
                                                  //Serial.println("1");                             // reply ACK to GUI  
                                              }

                                              if((SER_RXD_VAL != 0) && (SER_RXD_VAL != 1))
                                              {                                                 
                                                  //Serial.println("x");                             // reply ACK to GUI  
                                              } 
                                          break;
                                            
                                          

                                          case '2': // set audio path                                           
                                              rx_str = rx_str.substring(3);                         // strip off first 2 chars
                                              SER_RXD_VAL = rx_str.toInt();                         // assign newly rxd data to SER_RXD_VAL

                                              //  Serial.println();                                     // spacer
                                              // Serial.println("rx_str case 2:");                     // reply ACK to GUI
                                              //  Serial.println(SER_RXD_VAL);                          // reply ACK to GUI

                                              if(SER_RXD_VAL == 0)
                                              {
                                                  Set_Q2_State = 0;
                                                  //Serial.println("0");                             // reply ACK to GUI  
                                              }

                                              if(SER_RXD_VAL == 1)
                                              {
                                                  Set_Q2_State = 1;
                                                  //Serial.println("1");                             // reply ACK to GUI  
                                              }

                                              if((SER_RXD_VAL != 0) && (SER_RXD_VAL != 1))
                                              {                                                 
                                                  Serial.println("x");                             // reply ACK to GUI  
                                              } 
                                          break;

                                          case '3': // set audio path                                           
                                              rx_str = rx_str.substring(3);                         // strip off first 2 chars
                                              SER_RXD_VAL = rx_str.toInt();                         // assign newly rxd data to SER_RXD_VAL

                                             // Serial.println();                                     // spacer
                                             // Serial.println("rx_str case 3:");                     // reply ACK to GUI
                                             // Serial.println(SER_RXD_VAL);                          // reply ACK to GUI

                                              if(SER_RXD_VAL == 0)
                                              {
                                                  Set_Q3_State = 0;
                                                  //Serial.println("0");                             // reply ACK to GUI  
                                              }

                                              if(SER_RXD_VAL == 1)
                                              {
                                                  Set_Q3_State = 1;
                                                  //Serial.println("1");                             // reply ACK to GUI  
                                              }

                                              if((SER_RXD_VAL != 0) && (SER_RXD_VAL != 1))
                                              {                                                 
                                                  Serial.println("x");                             // reply ACK to GUI  
                                              } 
                                          break;
                                            
                                          


                                         case '4': // set audio path                                           
                                              rx_str = rx_str.substring(3);                         // strip off first 2 chars
                                              SER_RXD_VAL = rx_str.toInt();                         // assign newly rxd data to SER_RXD_VAL

                                              //Serial.println();                                     // spacer
                                             // Serial.println("rx_str case 4:");                     // reply ACK to GUI
                                              //Serial.println(SER_RXD_VAL);                          // reply ACK to GUI

                                              if(SER_RXD_VAL == 0)
                                              {
                                                  Set_Q4_State = 0;
                                                  //Serial.println("0");                             // reply ACK to GUI  
                                              }

                                              if(SER_RXD_VAL == 1)
                                              {
                                                  Set_Q4_State = 1;
                                                  //Serial.println("1");                             // reply ACK to GUI  
                                              }

                                              if((SER_RXD_VAL != 0) && (SER_RXD_VAL != 1))
                                              {                                                 
                                                  Serial.println("x");                             // reply ACK to GUI  
                                              } 

                                         break; //  case '4': 
                                                                                     
                                      } //switch(rx_arr[2])

                                  break; // case a; 
                                                                                                
                              }//  switch(rx_arr[1]) 
                                                                                              
                       break;  //case 's': // setters     

                                                                      
                                                 
                      

                      //****************************************  GETTERS    ****************************************************
                       
                       case 'g': // getters
                            // Serial2.println();                            // spacer
                            // rx_str = rx_str.substring(1);                   // strip off first 2 chars
                            // SER_RXD_VAL = rx_str.toInt();                   // assign newly rxd data to SER_RXD_VAL
                            switch(rx_arr[1])
                            {                    
                              case 'c': // count
                               switch(rx_arr[2])
                               {
                                  case '1': // count perch 1
                                    Serial.println(Perch_CH1_Count);  // bad entry response
                                  break;

                                  case '2': // count perch 2
                                    Serial.println(Perch_CH2_Count);  // bad entry response
                                  break;

                                  case '3': // count perch 3
                                    Serial.println(Perch_CH3_Count);  // bad entry response
                                  break;

                                  case '4': // count perch 4
                                    Serial.println(Perch_CH4_Count);  // bad entry response
                                  break;                                  
                               }                                                              
                              break; // Case C ==> get count
                            }
                       break;  // case g ==> getters         
                      
                    } // switch(rx_arr[0])   
                    
                  // RXD_CNT++;
                   rx_str = "";                                // clear the string for next packet/command
                   rx_index = 0;                               // reset array index to 0
                 
            } //else newline
                       
     } //while serial
  
}


// **************************************************************************************************************************************************
//                                                                      ReadSensors
// - 
// - 
// - 
// -
// **************************************************************************************************************************************************
void ReadSensors()
{
  if(LAT1_TMR > Max_Latency)
  {
    LAT1_TMR = Max_Latency;
  }

  if(LAT2_TMR > Max_Latency)
  {
    LAT2_TMR = Max_Latency;
  }

  if(LAT3_TMR > Max_Latency)
  {
    LAT3_TMR = Max_Latency;
  }
  if(LAT4_TMR > Max_Latency)
  {
    LAT4_TMR = Max_Latency;
  }
    
    
  if((UPD_SEN_CNT > UPD_SEN_INTVAL) && (RUNMODE))
  {    
    //digitalWrite(TPD_PIN, HIGH );                  //  SET RELAY
    // ----- PERCH SW-1 DETECT AND COUNT  -------
    Perch_SW1_State = digitalRead(Perch_SW1_PIN);
        
    if(!Perch_SW1_State)
    {
     /// Serial.println("SW1_ACC_TMR++...");  // bad entry response      
      SW1_ACC_TMR++;
    }
    else
    {
     // Serial.println("SW1_ACC_TMR--...");  // bad entry response      
      SW1_ACC_TMR--;
    }

    //Serial.print("SW1_ACC_TMR: ");  // bad entry response
    // Serial.println(SW1_ACC_TMR);  // bad entry response

    if(SW1_ACC_TMR < 1 )
    {
    //  Set_Q1_State = 0;      
      SW1_ACC_TMR = 0;

      Old_SW1_State = 1;
    }

    if(SW1_ACC_TMR > uint16_t(DEBOUNCE_DLY))
    {
      // Set_Q1_State = 1;
      
      if(Old_SW1_State == 1)
      {
          Perch_CH1_Count++;              //   

          LAT1_TMR = 0;  // reset counter for new timing run

          if(!POLL_MODE)
          {
            Serial.print("A");                                      // startup serial text 
            Serial.println(Perch_CH1_Count);                        // startup serial text 
          }

          EEPROM.write(NVM_CH1_CNT_ADR, Perch_CH1_Count);           //
          
          delay(10);                                                //

          Old_SW1_State = 0;
      }
      
      SW1_ACC_TMR = uint16_t(DEBOUNCE_DLY);
    }

    // ----- PERCH SW-2 DETECT AND COUNT  -------
    Perch_SW2_State = digitalRead(Perch_SW2_PIN);
    
    if(!Perch_SW2_State)
    {
      SW2_ACC_TMR++;
    }
    else
    {
      SW2_ACC_TMR--;
    }

    if(SW2_ACC_TMR < 1 )
    {
     //Set_Q2_State = 0;      
      SW2_ACC_TMR = 0;

      Old_SW2_State = 1;
    }

    if(SW2_ACC_TMR > uint16_t(DEBOUNCE_DLY))
    {
     // Set_Q2_State = 1;      
      if(Old_SW2_State == 1)
      {
          Perch_CH2_Count++;                                      //  

          LAT2_TMR = 0; // reset counter for new timing run

          if(!POLL_MODE)
          {
            Serial.print("B");                                      // startup serial text 
            Serial.println(Perch_CH2_Count);                        // startup serial text 
          }

          EEPROM.write(NVM_CH2_CNT_ADR, Perch_CH2_Count);           //
          
          delay(10);                                                //

          Old_SW2_State = 0;
      } 
      SW2_ACC_TMR = uint16_t(DEBOUNCE_DLY);
    }
   
    
    // ----- PERCH SW-3 DETECT AND COUNT  -------
    Perch_SW3_State = digitalRead(Perch_SW3_PIN);
    
    if(!Perch_SW3_State)
    {
      SW3_ACC_TMR++;
    }
    else
    {
      SW3_ACC_TMR--;
    }

    if(SW3_ACC_TMR < 1 )
    {
     // Set_Q3_State = 0;
      
      SW3_ACC_TMR = 0;

      Old_SW3_State = 1;
    }


    if(SW3_ACC_TMR > uint16_t(DEBOUNCE_DLY))
    {
     //  Set_Q3_State = 1;       
      if(Old_SW3_State == 1)
      {
          Perch_CH3_Count++;              // 

          LAT3_TMR = 0; // reset counter for new timing run

          if(!POLL_MODE)
          {
            Serial.print("C");                     // startup serial text 
            Serial.println(Perch_CH3_Count);                     // startup serial text 
          }

          EEPROM.write(NVM_CH3_CNT_ADR, Perch_CH3_Count);           //
          
          delay(10);                                                //

          Old_SW3_State = 0;
      }                 //      
      SW3_ACC_TMR = uint16_t(DEBOUNCE_DLY);
    }        

    // ----- PERCH SW-4 DETECT AND COUNT  -------
    Perch_SW4_State = digitalRead(Perch_SW4_PIN);
    
    if(!Perch_SW4_State)
    {
      SW4_ACC_TMR++;
    }
    else
    {
      SW4_ACC_TMR--;
    }

    if(SW4_ACC_TMR < 1 )
    {
     // Set_Q4_State = 0;
      
      SW4_ACC_TMR = 0;

      Old_SW4_State = 1;
    }


    if(SW4_ACC_TMR > uint16_t(DEBOUNCE_DLY))
    {
      //  Set_Q4_State = 1;      
      if(Old_SW4_State == 1)
      {
          Perch_CH4_Count++;              // 

          LAT4_TMR = 0; // reset counter for new timing run

          if(!POLL_MODE)
          {
            Serial.print("D");                     // startup serial text 
            Serial.println(Perch_CH4_Count);                     // startup serial text 
          }

          EEPROM.write(NVM_CH4_CNT_ADR, Perch_CH4_Count);           //
          
          delay(10);                                                //

          Old_SW4_State = 0;
      }                 //             // 
      
      SW4_ACC_TMR = uint16_t(DEBOUNCE_DLY);
    } 
  //  digitalWrite(TPD_PIN, LOW );                  //  SET RELAY  
  UPD_SEN_CNT = 0;
  }  
}


// **************************************************************************************************************************************************
//                                                                      SetOutputs
// - 
// - 
// - 
// -
// **************************************************************************************************************************************************
void SetOutputs()
{
  if(UPD_SOP_CNT > UPD_SOP_INTVAL)
  {
     // test
     // Set_Q1_State = !Set_Q1_State;
     // Set_Q2_State = !Set_Q2_State;
     // Set_Q3_State = !Set_Q3_State;
     // Set_Q4_State = !Set_Q4_State;       

     if(RUNMODE == 0)
     {   
        Set_Q1_State = 0;    
        Set_Q2_State = 0;    
        Set_Q3_State = 0;    
        Set_Q4_State = 0; 

        digitalWrite(ILED, LOW);      // internal LED OFF
     }
     else
     {
        digitalWrite(ILED, HIGH);    // internal LED ON (amber)
     }

     digitalWrite(SPK_Q1_PIN, Set_Q1_State);  
     digitalWrite(SPK_Q2_PIN, Set_Q2_State);  
     digitalWrite(SPK_Q3_PIN, Set_Q3_State);  
     digitalWrite(SPK_Q4_PIN, Set_Q4_State);     
  
     UPD_SOP_CNT = 0;                // reset schedule timer
  }

 
  
}


// **************************************************************************************************************************************************
//                                                                      SendSerial
// - Send serial strings to PC/USB
// - mode selects which mode is sending out (0=off, 1 = print ,2 = plotter)
// - 
// -
// **************************************************************************************************************************************************
void SendSerial()
{
  if(MSEC_CNT > 999)
  {
    MSEC_CNT = 0;
    Runtime++;
  }

  if(DBG_MODE == 1)
  {
     if(UPD_DBG_CNT > UPD_DBG_INTVAL)                 // Text debugger
     {
         Serial.println();                            // spacer   
         Serial.print("Runtime: ");                   // startup serial text   
         Serial.println(Runtime);                     // startup serial text 
         Serial.print("RUNMODE: ");                   // startup serial text   
         Serial.println(RUNMODE);                     // startup serial text 
         Serial.print("DEBOUNCE_DLY: ");                   // startup serial text   
         Serial.println(DEBOUNCE_DLY);                     // startup serial text 
         
         Serial.print("Perch_CH1_Count: ");           // startup serial text   
         Serial.println(Perch_CH1_Count);             // startup serial text 
         Serial.print("Set_Q1_State: ");              // startup serial text   
         Serial.println(Set_Q1_State);                // startup serial text
         Serial.print("Perch_SW1_State: ");           // startup serial text   
         Serial.println(Perch_SW1_State);             // startup serial text  
         Serial.print("SW1_ACC_TMR: ");               // startup serial text   
         Serial.println(SW1_ACC_TMR);                 // startup serial text

         Serial.print("Perch_CH2_Count: ");           // startup serial text   
         Serial.println(Perch_CH2_Count);             // startup serial text 
         Serial.print("Set_Q2_State: ");           // startup serial text   
         Serial.println(Set_Q2_State);             // startup serial text
         Serial.print("Perch_SW2_State: ");           // startup serial text   
         Serial.println(Perch_SW2_State);             // startup serial text 
         Serial.print("SW2_ACC_TMR: ");               // startup serial text   
         Serial.println(SW2_ACC_TMR);                 // startup serial text  

         Serial.print("Perch_CH3_Count: ");           // startup serial text   
         Serial.println(Perch_CH3_Count);             // startup serial text 
         Serial.print("Set_Q3_State: ");           // startup serial text   
         Serial.println(Set_Q3_State);             // startup serial text
         Serial.print("Perch_SW3_State: ");           // startup serial text   
         Serial.println(Perch_SW3_State);             // startup serial text
         Serial.print("SW3_ACC_TMR: ");               // startup serial text   
         Serial.println(SW3_ACC_TMR);                 // startup serial text   

         Serial.print("Perch_CH4_Count: ");           // startup serial text   
         Serial.println(Perch_CH4_Count);             // startup serial text 
         Serial.print("Set_Q4_State: ");           // startup serial text   
         Serial.println(Set_Q4_State);             // startup serial text
         Serial.print("Perch_SW4_State: ");           // startup serial text   
         Serial.println(Perch_SW4_State);             // startup serial text 
         Serial.print("SW4_ACC_TMR: ");               // startup serial text   
         Serial.println(SW4_ACC_TMR);                 // startup serial text            
    
         UPD_DBG_CNT = 0;                             // Reset counter
     }
  }

   if(DBG_MODE == 2) // plotter mode, plot sensor data if required
   {
      if(UPD_PLT_CNT > UPD_PLT_INTVAL)                // Text debugger
      {
         //Serial.println();                          // spacer   
         //Serial.print("Runtime: ");                 // startup serial text   
         //Serial.println(Runtime);                   // startup serial text 
         UPD_PLT_CNT = 0;                             // Reset counter
      }
   }  
}


//****************************************************************************************************************
//                                           MAIN LOOP
//   main loop / continous loop
// 
//****************************************************************************************************************

// the loop routine runs over and over again forever:
void loop()
{
  CheckSerial();               // check and parse serial input from USB/PC
  ReadSensors();               // Read out sensors/ perch micro switches
  SetOutputs();                // Set Relays and LED(s)
  SendSerial();                // Serial TXD/Debug routines (send to USB/PC) 
}

// ****************************************   Timer1 ISR (set to 1 mSec)  **************************************************************************
ISR(TIMER1_OVF_vect)            // ISR label for Timer1
{
  TCNT1 = 65473;                // reload timer1 ==> overflows every 1 mSec (62*16us)
  
  MSEC_CNT++;                   // update runtime/elapsed time timer 
  UPD_DBG_CNT++;                //  update debug interval timer/counter 
  UPD_SEN_CNT++;                //  update sensor interval timer/counter
  UPD_SOP_CNT++;                //  update sensor interval timer/counter   
  
  LAT1_TMR++;                   // Latency SW1
  LAT2_TMR++;                   // Latency SW2
  LAT3_TMR++;                   // Latency SW3
  LAT4_TMR++;                   // Latency SW4
} 

// ************************************************   END Timer1 ISR       **************************************************************************
