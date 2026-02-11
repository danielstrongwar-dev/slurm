#include <Servo.h>

// === Сервы (4 шт) ===
Servo servos[4];
const int servoPins[4] = {5, 6, 3, 4};  // пины Arduino Nano

// === PWM вход (AUX1 → D2) ===
volatile unsigned long pulseWidth = 0;
volatile unsigned long lastRise = 0;

// === Режимы ===
enum Mode { STOP, ALL_ON, SEQUENCE };
Mode currentMode = STOP;

// === Для последовательности ===
unsigned long lastStepTime = 0;
int step = 0;
const unsigned long STEP_DELAY = 2000; // 2 сек между шагами

void setup() {
  // Инициализация серв
  for (int i = 0; i < 4; i++) {
    servos[i].attach(servoPins[i]);
    servos[i].write(180); // исходное положение
  }

  // Настройка прерывания на D2
  pinMode(2, INPUT);
  attachInterrupt(digitalPinToInterrupt(2), readPWM, CHANGE);

  // Отладка (можно удалить)
  Serial.begin(115200);
}

void loop() {
  // Защита от шума
  if (pulseWidth < 900 || pulseWidth > 2100) return;

  // Определение режима по PWM
  if (pulseWidth > 1800) {
    currentMode = ALL_ON;
    step = 0;
  } else if (pulseWidth < 1200) {
    currentMode = SEQUENCE;
  } else {
    currentMode = STOP;
    step = 0;
  }

  // Выполнение
  switch (currentMode) {
    case STOP:
      for (int i = 0; i < 4; i++) servos[i].write(180);
      break;

    case ALL_ON:
      for (int i = 0; i < 4; i++) servos[i].write(0);
      break;

    case SEQUENCE:
      runSequence();
      break;
  }

  // Отладка (опционально)
  if (millis() % 1000 < 10) {
    Serial.print("PWM: "); Serial.print(pulseWidth);
    Serial.print(" | Mode: ");
    Serial.println(currentMode == STOP ? "STOP" : (currentMode == ALL_ON ? "ALL" : "SEQ"));
  }
}

// Прерывание для точного измерения PWM
void readPWM() {
  unsigned long now = micros();
  if (digitalRead(2) == HIGH) {
    lastRise = now;
  } else {
    pulseWidth = now - lastRise;
  }
}

void runSequence() {
  if (millis() - lastStepTime >= STEP_DELAY) {
    // Гасим все
    for (int i = 0; i < 4; i++) servos[i].write(180);

    // Включаем текущую
    if (step < 4) {
      servos[step].write(0);
      step++;
    } else {
      step = 0; // зациклить
    }

    lastStepTime = millis();
  }
}