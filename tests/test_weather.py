import csv

from mina.weather import HABITAT_SUBOPTIMAL_PERCENT, analyze


def _write_census(path):
    with path.open("w", newline="", encoding="utf-8") as handle:
        w = csv.writer(handle)
        w.writerow(["study_name","time","island_name","colony_code","num_breeding_pairs"])
        w.writerow(["","UTC","","","1"])
        islands = ["CHR","COR","HUM","LIT","TOR"]
        counts = {i:1000 + j*100 for j,i in enumerate(islands)}
        for year in range(1991, 2009):
            wet = year % 5
            for island in islands:
                h = HABITAT_SUBOPTIMAL_PERCENT[island]
                if year > 1991:
                    counts[island] *= 0.96 * (1 - 0.0005 * h * wet)
                total=max(0, round(counts[island]))
                w.writerow([f"PAL{year}",f"{year}-11-15T00:00:00Z",island,"1",total])


def _write_weather(path):
    with path.open("w", newline="", encoding="utf-8") as handle:
        w=csv.writer(handle)
        w.writerow(["Date","Precipitation_melted_mm","AirTemp"])
        for year in range(1989, 2010):
            wet=year % 5
            for day in range(1,32):
                p=1.0 if day <= 5 + wet else 0.0
                w.writerow([f"{year}-10-{day:02d}",p,-3])


def test_weather_habitat_pipeline(tmp_path):
    census=tmp_path/"census.csv"
    weather=tmp_path/"weather.csv"
    _write_census(census)
    _write_weather(weather)
    result=analyze(census,weather)
    assert result["model"]["interaction_coefficient"] < 0
    assert result["model"]["directional_prediction_met"] is True
    assert result["weather_schema"]["date_field"] == "Date"
    assert result["weather_schema"]["precipitation_field"] == "Precipitation_melted_mm"
