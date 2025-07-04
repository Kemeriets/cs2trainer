from fastapi import FastAPI
import requests
import openai
import json
import os

app = FastAPI()

# ➤ ТВОИ КЛЮЧИ
FACEIT_API_KEY = os.getenv("FACEIT_API_KEY")
FACEIT_BASE_URL = "https://open.faceit.com/data/v4/"
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
openai.api_key = OPENAI_API_KEY

# ➤ Главная страница
@app.get("/")
def root():
    return {"message": "CS2 Trainer API работает ✅"}

# ➤ Приветствие
@app.get("/hello")
def hello(name: str):
    return {"message": f"Привет, {name}!"}

# ➤ Получить профиль Faceit
@app.get("/player/stats/faceit")
def get_faceit_player(nickname: str):
    headers = {"Authorization": f"Bearer {FACEIT_API_KEY}"}
    response = requests.get(FACEIT_BASE_URL + f"players?nickname={nickname}", headers=headers)

    if response.status_code != 200:
        return {"error": f"Faceit API вернул ошибку: {response.status_code}"}

    player_data = response.json()

    return {
        "nickname": player_data.get("nickname"),
        "country": player_data.get("country"),
        "games": player_data.get("games"),
        "faceit_elo": player_data.get("games", {}).get("cs2", {}).get("faceit_elo"),
        "skill_level": player_data.get("games", {}).get("cs2", {}).get("skill_level"),
        "avatar": player_data.get("avatar"),
        "player_id": player_data.get("player_id")
    }

# ➤ Получить историю матчей
@app.get("/player/matches/faceit")
def get_faceit_matches(player_id: str, game: str = "cs2", limit: int = 5):
    headers = {"Authorization": f"Bearer {FACEIT_API_KEY}"}
    response = requests.get(FACEIT_BASE_URL + f"players/{player_id}/history?game={game}&limit={limit}", headers=headers)

    if response.status_code != 200:
        return {"error": f"Faceit API вернул ошибку: {response.status_code}"}

    return response.json()

# ➤ GPT-анализ профиля
@app.post("/player/analyze")
def analyze_player(player_data: dict):
    prompt = f"Ты профессиональный тренер по CS2. Проанализируй данные игрока и составь советы по улучшению. Данные игрока: {player_data}"

    # Новый клиент OpenAI
    client = openai.OpenAI(api_key=OPENAI_API_KEY)

    # Новый вызов chat completion
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "Ты профессиональный тренер по CS2."},
            {"role": "user", "content": prompt}
        ]
    )

    return {"analysis": response.choices[0].message.content}
# ➤ Сохранить профиль в JSON
@app.post("/player/profile/save")
def save_profile(player_data: dict):
    nickname = player_data.get("nickname", "unknown_player")
    filename = f"{nickname}_profile.json"

    with open(filename, "w", encoding="utf-8") as f:
        json.dump(player_data, f, indent=4, ensure_ascii=False)

    return {"message": f"Профиль игрока {nickname} сохранён в {filename}"}
