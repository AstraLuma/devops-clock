#include <Arduino.h>
#include <TM1640.h>
#include <TM16xxMatrix.h>

TM1640 module(8, 9); // DIO=8, CLK=9
#define MATRIX_NUMCOLUMNS 16
#define MATRIX_NUMROWS 8
TM16xxMatrix matrix(&module, MATRIX_NUMCOLUMNS, MATRIX_NUMROWS); // TM16xx object, columns, rows

void setup()
{
  Serial.begin(9600);
  matrix.setAll(true);
}

void loop()
{
  for(uint8_t blnk = 0; blnk < 5; blnk ++){
    digitalWrite(LED_BUILTIN,true);
    delay(500);
    digitalWrite(LED_BUILTIN,false);
    delay(500);
  }
  matrix.setAll(false); // set all pixels off
  Serial.println("Starting Matrix test...");
  for (uint8_t row = 0; row < MATRIX_NUMROWS; row++)
  {
    for (uint8_t col = 0; col < MATRIX_NUMCOLUMNS; col++)
    {
      Serial.print(F("Checking segment ("));
      Serial.print(col);
      Serial.print(",");
      Serial.print(row);
      Serial.println(")");
      matrix.setPixel(col, row, true); // set one pixel on
      while (!Serial.available())
      {
      }
      Serial.read();
      while (!Serial.available())
      {
      }
      Serial.read();
      matrix.setPixel(col, row, false); // set another pixel off
    }
  }
  matrix.setAll(true);
}