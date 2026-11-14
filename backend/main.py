import math
import random
from typing import List, Dict, Optional
from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

app = FastAPI(title="SPHEREx CHRONOS API — NASA Space Apps 2026")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Реальные астрономические данные для 5 тестовых объектов из задания NASA
TARGETS_DB = {
    "wise0855": {
        "id": "wise0855",
        "name": "WISE 0855 (Brown Dwarf)",
        "ra_str": "08h55m10.831s",
        "dec_str": "-7d14m42.53s",
        "ra_deg": 133.79513,
        "dec_deg": -7.24515,
        "pm_ra_arcsec_yr": -8.1,   # Огромное собственное движение
        "pm_dec_arcsec_yr": 0.7,
        "molecules": "Water Ice & Methane (H2O, CH4)",
        "contamination_flag": "CLEAN (0x00)",
        "category": {
            "en": "Fast-moving Cold Brown Dwarf",
            "ru": "Быстродвижущийся холодный коричневый карлик",
            "kk": "Жылдам қозғалатын суық қоңыр ергежейлі"
        },
        "fact": {
            "en": "WISE 0855 is the coldest known brown dwarf (~250 K / -23°C) — as chilly as Earth's North Pole, yet 3 to 10 times more massive than Jupiter, drifting just 7.4 light-years away.",
            "ru": "WISE 0855 — самый холодный из известных коричневых карликов (-23°C), холодный как Северный полюс Земли, но в 3–10 раз массивнее Юпитера и летит всего в 7.4 световых годах от нас.",
            "kk": "WISE 0855 — белгілі ең суық қоңыр ергежейлі (-23°C), Жердің Солтүстік полюсіндей суық, бірақ Юпитерден 3-10 есе ауыр және бізден небәрі 7.4 жарық жылы қашықтықта орналасқан."
        },
        "light_curve": [1.000, 1.048, 1.026, 0.966],
        "spectral_profile": "ch4_h2o"
    },
    "barnard": {
        "id": "barnard",
        "name": "Barnard's Star",
        "ra_str": "17h57m48.498s",
        "dec_str": "+04d41m36.11s",
        "ra_deg": 269.45207,
        "dec_deg": 4.69336,
        "pm_ra_arcsec_yr": -0.80,
        "pm_dec_arcsec_yr": 10.36, # Рекордное движение по небу
        "molecules": "Water Vapor & Iron Hydride (H2O, FeH)",
        "contamination_flag": "CLEAN (0x00)",
        "category": {
            "en": "High-Proper-Motion Red Dwarf",
            "ru": "Красный карлик с рекордным движением",
            "kk": "Өзіндік қозғалысы өте жоғары қызыл ергежейлі"
        },
        "fact": {
            "en": "Barnard's Star races across Earth's sky faster than any other star — moving the width of a full Moon every 180 years. It hosts a sub-Earth exoplanet (Barnard b) orbiting in 3.15 days.",
            "ru": "Звезда Барнарда мчится по небу быстрее всех звезд — она проходит диаметр полной Луны каждые 180 лет. Вокруг нее вращается экзопланета легче Земли с годом в 3.15 дня.",
            "kk": "Барнард жұлдызы аспанда барлық жұлдыздардан жылдам қозғалады — әр 180 жыл сайын толық Айдың диаметріндей қашықтықты жүріп өтеді. Оны Жерден жеңіл экзопланета айналып жүреді."
        },
        "light_curve": [1.000, 0.992, 1.015, 0.988],
        "spectral_profile": "red_dwarf"
    },
    "eps_indi": {
        "id": "eps_indi",
        "name": "Epsilon Indi B (Ba/Bb)",
        "ra_str": "22h04m10.520s",
        "dec_str": "-56d46m57.70s",
        "ra_deg": 331.04383,
        "dec_deg": -56.78269,
        "pm_ra_arcsec_yr": 3.96,
        "pm_dec_arcsec_yr": -2.53,
        "molecules": "Ammonia, Methane & CO (NH3, CH4, CO)",
        "contamination_flag": "BINARY_BLEND (0x02)",
        "category": {
            "en": "Binary Brown Dwarf System",
            "ru": "Двойная система коричневых карликов",
            "kk": "Қос қоңыр ергежейлілер жүйесі"
        },
        "fact": {
            "en": "Epsilon Indi B is actually a pair of failed stars (Ba and Bb) orbiting each other every 11 years while together circling a bright orange star 11.9 light-years from Earth.",
            "ru": "Эпсилон Индейца B — это пара «неудавшихся звезд», вращающихся друг вокруг друга за 11 лет, и вместе облетающих яркую оранжевую звезду в 11.9 световых годах от Земли.",
            "kk": "Эпсилон Үнді B — бір-бірін 11 жылда айналып шығатын екі «сәтсіз жұлдыз» жұбы, олар бірге Жерден 11.9 жарық жылы қашықтықтағы қызғылт сары жұлдызды айналады."
        },
        "light_curve": [1.000, 1.031, 0.974, 1.019],
        "spectral_profile": "nh3_ch4"
    },
    "rw_aur": {
        "id": "rw_aur",
        "name": "RW Aurigae",
        "ra_str": "05h07m49.538s",
        "dec_str": "+30d24m05.07s",
        "ra_deg": 76.95641,
        "dec_deg": 30.40141,
        "pm_ra_arcsec_yr": 0.01,
        "pm_dec_arcsec_yr": -0.02,
        "molecules": "Silicate Dust, H2O & CO Emission",
        "contamination_flag": "DISK_VAR (0x04)",
        "category": {
            "en": "Young Variable Star with Dust Disk",
            "ru": "Молодая переменная звезда с пылевым диском",
            "kk": "Шаңды дискісі бар жас айнымалы жұлдыз"
        },
        "fact": {
            "en": "RW Aurigae is only a few million years old. Giant clouds of planetary building blocks periodically eclipse the star, causing its infrared brightness to fluctuate dramatically.",
            "ru": "Звезде RW Возничего всего несколько миллионов лет. Гигантские облака протопланетной пыли периодически затмевают её, вызывая резкие скачки инфракрасного блеска.",
            "kk": "RW Арбакеш жұлдызы небәрі бірнеше миллион жаста. Протопланеталық шаң бұлттары жұлдызды мезгіл-мезгіл көлегейлеп, оның инфрақызыл жарықтығын күрт өзгертеді."
        },
        "light_curve": [1.000, 0.640, 1.180, 0.790],
        "spectral_profile": "silicate_disk"
    },
    "r_draconis": {
        "id": "r_draconis",
        "name": "R Draconis",
        "ra_str": "16h32m40.230s",
        "dec_str": "+66d45m17.90s",
        "ra_deg": 248.16762,
        "dec_deg": 66.75497,
        "pm_ra_arcsec_yr": -0.01,
        "pm_dec_arcsec_yr": 0.01,
        "molecules": "Water Vapor & Carbon Monoxide (H2O, CO)",
        "contamination_flag": "BRIGHT_SAT (0x01)",
        "category": {
            "en": "Mira-Type Pulsating Red Giant",
            "ru": "Пульсирующий красный гигант типа Миры",
            "kk": "Мира типті пульсацияланатын қызыл алып"
        },
        "fact": {
            "en": "R Draconis is an aging red giant that swells and shrinks every 245 days, changing its brightness by over 100 times in visible light while shedding water-rich gas into space.",
            "ru": "R Дракона — стареющий красный гигант, который раздувается и сжимается каждые 245 дней, меняя блеск более чем в 100 раз и выбрасывая в космос богатый водой газ.",
            "kk": "R Айдаһар — әр 245 күн сайын ісініп, кішірейетін қартайған қызыл алып. Ол жарықтығын 100 еседен астам өзгертіп, ғарышқа суға бай газ шашады."
        },
        "light_curve": [1.000, 1.420, 0.580, 1.290],
        "spectral_profile": "mira_giant"
    }
}

def generate_102_bands(profile: str) -> List[Dict]:
    """Генерирует 102 спектральные полосы SPHEREx (0.75 - 5.00 мкм, 6 детекторов)"""
    bands = []
    for i in range(102):
        # Логарифмическая шкала длин волн SPHEREx от 0.75 до 5.00 мкм
        wl = round(0.75 * ((5.00 / 0.75) ** (i / 101.0)), 3)
        array_id = min(6, (i // 17) + 1)
        
        base = 0.72 + 0.12 * math.sin(i * 0.18)
        if profile == "ch4_h2o":
            # Глубокие полосы поглощения воды (1.4, 1.9, 2.7 мкм) и метана (3.3 мкм)
            if abs(wl - 1.40) < 0.12 or abs(wl - 1.90) < 0.14 or abs(wl - 2.70) < 0.18:
                base -= 0.34
            if abs(wl - 3.32) < 0.22:
                base -= 0.38
        elif profile == "red_dwarf":
            base = 0.88 - (wl - 0.75) * 0.08 + 0.06 * math.cos(i * 0.25)
            if abs(wl - 1.45) < 0.15:
                base -= 0.16
        elif profile == "nh3_ch4":
            if abs(wl - 1.52) < 0.12 or abs(wl - 2.25) < 0.15 or abs(wl - 3.30) < 0.2:
                base -= 0.29
        elif profile == "silicate_disk":
            # Эмиссия пыли на длинных волнах (> 3.0 мкм)
            base = 0.55 + (wl / 5.0) * 0.38 + 0.05 * math.sin(i * 0.3)
        elif profile == "mira_giant":
            base = 0.80 + 0.15 * math.sin(i * 0.12)
            if abs(wl - 2.35) < 0.15 or abs(wl - 4.65) < 0.2:
                base -= 0.25

        flux = round(max(0.12, min(0.98, base + random.uniform(-0.025, 0.025))), 3)
        bands.append({
            "band": i + 1,
            "wavelength": wl,
            "array": array_id,
            "flux": flux
        })
    return bands

@app.get("/api/targets")
def get_targets():
    return list(TARGETS_DB.values())

@app.get("/api/sky-patch")
def get_sky_patch(
    target_id: str = Query("wise0855"),
    ra: Optional[float] = None,
    dec: Optional[float] = None,
    fov: float = Query(1.0, ge=0.2, le=5.0)
):
    target = TARGETS_DB.get(target_id, TARGETS_DB["wise0855"]).copy()
    center_ra = ra if ra is not None else target["ra_deg"]
    center_dec = dec if dec is not None else target["dec_deg"]

    # Генерируем 4 эпохи наблюдений SPHEREx (каждые 6 месяцев: 2025-05, 2025-11, 2026-05, 2026-11)
    epochs_labels = ["2025-05 (Epoch 1)", "2025-11 (Epoch 2)", "2026-05 (Epoch 3)", "2026-11 (Epoch 4)"]
    trajectory = []
    for idx, label in enumerate(epochs_labels):
        dt_years = idx * 0.5
        # Усиливаем визуальное смещение для наглядности на FOV, сохраняя точные астрометрические дельты
        dra_arcsec = round(target["pm_ra_arcsec_yr"] * dt_years, 2)
        ddec_arcsec = round(target["pm_dec_arcsec_yr"] * dt_years, 2)
        trajectory.append({
            "epoch_index": idx,
            "label": label,
            "delta_ra_arcsec": dra_arcsec,
            "delta_dec_arcsec": ddec_arcsec,
            "norm_x": round((dra_arcsec / 15.0) / fov, 4),
            "norm_y": round((ddec_arcsec / 15.0) / fov, 4),
            "flux_multiplier": target["light_curve"][idx]
        })

    # Фоновые звезды (Gaia DR3 / WISE) + 1 скрытый некаталогизированный движущийся объект (астероид / кандидат)
    rng = random.Random(int(abs(center_ra * 1000 + center_dec * 100)))
    background_objects = []
    for i in range(45):
        bx = round(rng.uniform(-0.85, 0.85), 4)
        by = round(rng.uniform(-0.85, 0.85), 4)
        catalog = "Gaia DR3" if i % 2 == 0 else "AllWISE"
        background_objects.append({
            "id": f"BG-{1000+i}",
            "name": f"{catalog} J{abs(int(center_ra))}{100+i}",
            "x": bx,
            "y": by,
            "z": round(rng.uniform(-0.35, 0.35), 4),
            "mag": round(rng.uniform(11.5, 19.8), 1),
            "catalog": catalog,
            "is_moving": False,
            "spectral_type": rng.choice(["G2V", "K5V", "M3V", "A0V", "F8V"])
        })

    # Скрытый движущийся кандидат для функции "Автопоиск движущихся объектов"
    hidden_mover = {
        "id": "CANDIDATE-X1",
        "name": "SPHEREx Moving Candidate #1",
        "start_x": -0.38,
        "start_y": 0.28,
        "vx_per_epoch": 0.14,
        "vy_per_epoch": -0.11,
        "z": 0.08,
        "mag": 17.4,
        "catalog": "UNCATALOGED (SPHEREx)",
        "is_moving": True,
        "spectral_type": "T-Dwarf / NEO Candidate"
    }

    return {
        "target": target,
        "center_ra": center_ra,
        "center_dec": center_dec,
        "fov": fov,
        "trajectory": trajectory,
        "spectrum_102": generate_102_bands(target["spectral_profile"]),
        "background_objects": background_objects,
        "hidden_mover": hidden_mover
    }

class DiscoveryReport(BaseModel):
    target_id: str
    ra: str
    dec: str
    classification: str
    marked_circles: list
    notes: Optional[str] = ""

@app.post("/api/discoveries")
def log_discovery(report: DiscoveryReport):
    return {
        "status": "recorded",
        "mission": "NASA SPHEREx 102-Band All-Sky Survey",
        "payload": report.dict()
    }