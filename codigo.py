# =========================================================
# SISTEMA COM FILTRO TEMPORAL + TEMPO MÍNIMO DE SERVO
# =========================================================


# ---------------------------------------------------------
# CONTROLE GERAL
# ---------------------------------------------------------
Move = False


# ---------------------------------------------------------
# AJUSTES FINOS
# ---------------------------------------------------------
DETECTION_CONFIRM_TIME = 150   # ms (validação da HuskyLens)
SERVO_HOLD_TIME = 250          # ms (tempo mínimo do servo ativo)


# ---------------------------------------------------------
# CONTROLE DE TEMPO
# ---------------------------------------------------------
last_id1_time = 0
last_id2_time = 0
servo_start_time = 0
servo_active = False


# ---------------------------------------------------------
# SERVO (RAMPA)
# ---------------------------------------------------------
SERVO_PIN = DigitalPin.P1
SERVO_CENTER = 90
SERVO_RIGHT = 140


# ---------------------------------------------------------
# RELÉ (ESTEIRA)
# ---------------------------------------------------------
RELAY_PIN = DigitalPin.P2


# ---------------------------------------------------------
# HUSKYLENS
# ---------------------------------------------------------
huskylens.init_i2c()
huskylens.init_mode(protocolAlgorithm.ALGORITHM_COLOR_RECOGNITION)


# ---------------------------------------------------------
# ESTADO INICIAL
# ---------------------------------------------------------
basic.clear_screen()
basic.show_icon(IconNames.HAPPY)

pins.servo_write_pin(SERVO_PIN, SERVO_CENTER)
pins.digital_write_pin(RELAY_PIN, 0)


# ---------------------------------------------------------
# BOTÃO A — ATIVA SISTEMA
# ---------------------------------------------------------
def on_button_pressed_a():
    global Move
    Move = True
    pins.digital_write_pin(RELAY_PIN, 1)

    basic.show_icon(IconNames.YES)
    basic.pause(400)
    basic.clear_screen()

input.on_button_pressed(Button.A, on_button_pressed_a)


# ---------------------------------------------------------
# BOTÃO B — DESATIVA SISTEMA
# ---------------------------------------------------------
def on_button_pressed_b():
    global Move, servo_active
    Move = False
    servo_active = False

    pins.digital_write_pin(RELAY_PIN, 0)
    pins.servo_write_pin(SERVO_PIN, SERVO_CENTER)

    basic.show_icon(IconNames.NO)
    basic.pause(400)
    basic.clear_screen()

input.on_button_pressed(Button.B, on_button_pressed_b)


# ---------------------------------------------------------
# LOOP PRINCIPAL
# ---------------------------------------------------------
def on_forever():
    global Move, last_id1_time, last_id2_time
    global servo_active, servo_start_time

    huskylens.request()
    now = control.millis()

    if Move:

        # -------------------------------------------------
        # ID2 — PARADA DE EMERGÊNCIA
        # -------------------------------------------------
        if huskylens.is_appear(2, HUSKYLENSResultType_t.HUSKYLENS_RESULT_BLOCK):

            if last_id2_time == 0:
                last_id2_time = now

            elif now - last_id2_time >= DETECTION_CONFIRM_TIME:
                Move = False
                servo_active = False

                pins.digital_write_pin(RELAY_PIN, 0)
                pins.servo_write_pin(SERVO_PIN, SERVO_CENTER)

                basic.show_icon(IconNames.NO)
                basic.pause(400)
                basic.clear_screen()

                last_id2_time = 0

        else:
            last_id2_time = 0


        # -------------------------------------------------
        # ID1 — ATIVA SERVO COM HOLD TIME
        # -------------------------------------------------
        if huskylens.is_appear(1, HUSKYLENSResultType_t.HUSKYLENS_RESULT_BLOCK):

            if last_id1_time == 0:
                last_id1_time = now

            elif now - last_id1_time >= DETECTION_CONFIRM_TIME and not servo_active:
                servo_active = True
                servo_start_time = now
                pins.servo_write_pin(SERVO_PIN, SERVO_RIGHT)

        else:
            last_id1_time = 0


        # -------------------------------------------------
        # CONTROLE DO TEMPO MÍNIMO DO SERVO
        # -------------------------------------------------
        if servo_active:
            if now - servo_start_time >= SERVO_HOLD_TIME:
                servo_active = False
                pins.servo_write_pin(SERVO_PIN, SERVO_CENTER)

    else:
        pins.servo_write_pin(SERVO_PIN, SERVO_CENTER)


basic.forever(on_forever)
