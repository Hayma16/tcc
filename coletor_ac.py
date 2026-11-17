"""
coletor_ac.py
─────────────
Coleta dados em tempo real do Assetto Corsa (original) via Shared Memory.
Salva em dados_ac.csv enquanto você joga.

Como usar:
  1. Abra o Assetto Corsa e entre em uma sessão
  2. Rode: python coletor_ac.py
  3. Dirija normalmente — os dados são gravados automaticamente
  4. Pressione Ctrl+C para parar
  5. Rode o dashboard: streamlit run app.py

Requisitos:
  pip install pywin32 pandas
"""

import ctypes
import mmap
import time
import csv
import os
from datetime import datetime


# ── Estruturas da Shared Memory do AC Original ─────────────────────────────

class SPageFilePhysics(ctypes.Structure):
    _fields_ = [
        ("packetId",              ctypes.c_int),
        ("gas",                   ctypes.c_float),
        ("brake",                 ctypes.c_float),
        ("fuel",                  ctypes.c_float),
        ("gear",                  ctypes.c_int),
        ("rpms",                  ctypes.c_int),
        ("steerAngle",            ctypes.c_float),
        ("speedKmh",              ctypes.c_float),
        ("velocity",              ctypes.c_float * 3),
        ("accG",                  ctypes.c_float * 3),
        ("wheelSlip",             ctypes.c_float * 4),
        ("wheelLoad",             ctypes.c_float * 4),
        ("wheelsPressure",        ctypes.c_float * 4),
        ("wheelAngularSpeed",     ctypes.c_float * 4),
        ("tyreWear",              ctypes.c_float * 4),
        ("tyreDirtyLevel",        ctypes.c_float * 4),
        ("tyreCoreTemperature",   ctypes.c_float * 4),
        ("camberRAD",             ctypes.c_float * 4),
        ("suspensionTravel",      ctypes.c_float * 4),
        ("drs",                   ctypes.c_float),
        ("tc",                    ctypes.c_float),
        ("heading",               ctypes.c_float),
        ("pitch",                 ctypes.c_float),
        ("roll",                  ctypes.c_float),
        ("cgHeight",              ctypes.c_float),
        ("carDamage",             ctypes.c_float * 5),
        ("numberOfTyresOut",      ctypes.c_int),
        ("pitLimiterOn",          ctypes.c_int),
        ("abs",                   ctypes.c_float),
        ("kersCharge",            ctypes.c_float),
        ("kersInput",             ctypes.c_float),
        ("autoShifterOn",         ctypes.c_int),
        ("rideHeight",            ctypes.c_float * 2),
        ("turboBoost",            ctypes.c_float),
        ("ballast",               ctypes.c_float),
        ("airDensity",            ctypes.c_float),
        ("airTemp",               ctypes.c_float),
        ("roadTemp",              ctypes.c_float),
        ("localAngularVel",       ctypes.c_float * 3),
        ("finalFF",               ctypes.c_float),
        ("performanceMeter",      ctypes.c_float),
        ("engineBrake",           ctypes.c_int),
        ("ersRecoveryLevel",      ctypes.c_int),
        ("ersPowerLevel",         ctypes.c_int),
        ("ersHeatCharging",       ctypes.c_int),
        ("ersIsCharging",         ctypes.c_int),
        ("kersCurrentKJ",         ctypes.c_float),
        ("drsAvailable",          ctypes.c_int),
        ("drsEnabled",            ctypes.c_int),
        ("brakeTemp",             ctypes.c_float * 4),
        ("clutch",                ctypes.c_float),
        ("tyreTempI",             ctypes.c_float * 4),
        ("tyreTempM",             ctypes.c_float * 4),
        ("tyreTempO",             ctypes.c_float * 4),
        ("isAIControlled",        ctypes.c_int),
        ("tyreContactPoint",      ctypes.c_float * 4 * 3),
        ("tyreContactNormal",     ctypes.c_float * 4 * 3),
        ("tyreContactHeading",    ctypes.c_float * 4 * 3),
        ("brakeBias",             ctypes.c_float),
        ("localVelocity",         ctypes.c_float * 3),
    ]


class SPageFileGraphic(ctypes.Structure):
    _fields_ = [
        ("packetId",              ctypes.c_int),
        ("status",                ctypes.c_int),
        ("session",               ctypes.c_int),
        ("currentTime",           ctypes.c_wchar * 15),
        ("lastTime",              ctypes.c_wchar * 15),
        ("bestTime",              ctypes.c_wchar * 15),
        ("split",                 ctypes.c_wchar * 15),
        ("completedLaps",         ctypes.c_int),
        ("position",              ctypes.c_int),
        ("iCurrentTime",          ctypes.c_int),
        ("iLastTime",             ctypes.c_int),
        ("iBestTime",             ctypes.c_int),
        ("sessionTimeLeft",       ctypes.c_float),
        ("distanceTraveled",      ctypes.c_float),
        ("isInPit",               ctypes.c_int),
        ("currentSectorIndex",    ctypes.c_int),
        ("lastSectorTime",        ctypes.c_int),
        ("numberOfLaps",          ctypes.c_int),
        ("tyreCompound",          ctypes.c_wchar * 33),
        ("replayTimeMultiplier",  ctypes.c_float),
        ("normalizedCarPosition", ctypes.c_float),
        ("carCoordinates",        ctypes.c_float * 3),
        ("penaltyTime",           ctypes.c_float),
        ("flag",                  ctypes.c_int),
        ("idealLineOn",           ctypes.c_int),
        ("isInPitLane",           ctypes.c_int),
        ("surfaceGrip",           ctypes.c_float),
        ("mandatoryPitDone",      ctypes.c_int),
        ("windSpeed",             ctypes.c_float),
        ("windDirection",         ctypes.c_float),
    ]


# ── Funções auxiliares ──────────────────────────────────────────────────────

def abrir_shared_memory():
    try:
        physics_mm = mmap.mmap(-1, ctypes.sizeof(SPageFilePhysics),
                               "Local\\acpmf_physics")
        graphics_mm = mmap.mmap(-1, ctypes.sizeof(SPageFileGraphic),
                                "Local\\acpmf_graphics")
        return physics_mm, graphics_mm
    except Exception:
        return None, None


def ler_physics(mm):
    mm.seek(0)
    return SPageFilePhysics.from_buffer_copy(mm.read(ctypes.sizeof(SPageFilePhysics)))


def ler_graphics(mm):
    mm.seek(0)
    return SPageFileGraphic.from_buffer_copy(mm.read(ctypes.sizeof(SPageFileGraphic)))


def marcha_display(gear_raw):
    if gear_raw == 0:
        return "R"
    elif gear_raw == 1:
        return "N"
    else:
        return str(gear_raw - 1)


# ── Coletor principal ───────────────────────────────────────────────────────

OUTPUT_FILE = "dados_ac.csv"
INTERVALO   = 0.1   # 10 Hz
VEL_MINIMA  = 1.0   # ignora registros parado

COLUNAS = [
    "timestamp", "volta", "tempo_volta_ms", "posicao_pista",
    "velocidade_kmh", "rpm", "marcha",
    "acelerador", "freio", "embreagem",
    "forca_g_lat", "forca_g_lon",
    "temp_pneu_fl", "temp_pneu_fr", "temp_pneu_rl", "temp_pneu_rr",
    "temp_freio_fl", "temp_freio_fr", "temp_freio_rl", "temp_freio_rr",
    "desgaste_pneu_fl", "desgaste_pneu_fr", "desgaste_pneu_rl", "desgaste_pneu_rr",
    "abs_ativo", "tc_ativo", "turbo_boost", "distancia_total_m",
]


def coletar():
    print("=" * 60)
    print("  Coletor de Telemetria — Assetto Corsa (original)")
    print("=" * 60)
    print(f"  Arquivo : {OUTPUT_FILE} | Intervalo: {INTERVALO}s")
    print("  Aguardando o AC iniciar uma sessão... (Ctrl+C para parar)\n")

    physics_mm, graphics_mm = None, None
    while physics_mm is None:
        physics_mm, graphics_mm = abrir_shared_memory()
        if physics_mm is None:
            print("  AC não detectado — tentando novamente em 3s...", end="\r")
            time.sleep(3)

    print("\n  Shared Memory aberta! Aguardando sessão ativa...\n")

    arquivo_novo = not os.path.exists(OUTPUT_FILE)
    registros    = 0
    ultimo_pacote = -1

    with open(OUTPUT_FILE, "a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=COLUNAS)
        if arquivo_novo:
            writer.writeheader()

        try:
            while True:
                p = ler_physics(physics_mm)
                g = ler_graphics(graphics_mm)

                # status 2 = sessão ao vivo
                if g.status != 2:
                    time.sleep(0.5)
                    continue

                if p.packetId == ultimo_pacote or p.speedKmh < VEL_MINIMA:
                    time.sleep(INTERVALO)
                    continue

                ultimo_pacote = p.packetId

                linha = {
                    "timestamp":         datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3],
                    "volta":             g.completedLaps + 1,
                    "tempo_volta_ms":    g.iCurrentTime,
                    "posicao_pista":     round(g.normalizedCarPosition, 4),
                    "velocidade_kmh":    round(p.speedKmh, 2),
                    "rpm":               p.rpms,
                    "marcha":            marcha_display(p.gear),
                    "acelerador":        round(p.gas, 3),
                    "freio":             round(p.brake, 3),
                    "embreagem":         round(p.clutch, 3),
                    "forca_g_lat":       round(p.accG[0], 3),
                    "forca_g_lon":       round(p.accG[2], 3),
                    "temp_pneu_fl":      round(p.tyreCoreTemperature[0], 1),
                    "temp_pneu_fr":      round(p.tyreCoreTemperature[1], 1),
                    "temp_pneu_rl":      round(p.tyreCoreTemperature[2], 1),
                    "temp_pneu_rr":      round(p.tyreCoreTemperature[3], 1),
                    "temp_freio_fl":     round(p.brakeTemp[0], 1),
                    "temp_freio_fr":     round(p.brakeTemp[1], 1),
                    "temp_freio_rl":     round(p.brakeTemp[2], 1),
                    "temp_freio_rr":     round(p.brakeTemp[3], 1),
                    "desgaste_pneu_fl":  round(p.tyreWear[0], 3),
                    "desgaste_pneu_fr":  round(p.tyreWear[1], 3),
                    "desgaste_pneu_rl":  round(p.tyreWear[2], 3),
                    "desgaste_pneu_rr":  round(p.tyreWear[3], 3),
                    "abs_ativo":         int(p.abs > 0.1),
                    "tc_ativo":          int(p.tc > 0.1),
                    "turbo_boost":       round(p.turboBoost, 3),
                    "distancia_total_m": round(g.distanceTraveled, 1),
                }

                writer.writerow(linha)
                f.flush()
                registros += 1

                if registros % 100 == 0:
                    print(f"  [{datetime.now().strftime('%H:%M:%S')}] "
                          f"Volta {g.completedLaps + 1} | "
                          f"{p.speedKmh:.0f} km/h | "
                          f"{p.rpms} RPM | "
                          f"Marcha {marcha_display(p.gear)} | "
                          f"{registros} registros")

                time.sleep(INTERVALO)

        except KeyboardInterrupt:
            print(f"\n\n  Coleta encerrada. Total de registros: {registros}")
            print(f"  Arquivo salvo: {OUTPUT_FILE}")

    physics_mm.close()
    graphics_mm.close()


if __name__ == "__main__":
    coletar()