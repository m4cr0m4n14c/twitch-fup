import json
import requests
import sys
import telegram
from dotenv import load_dotenv
import os
import asyncio

# Load environment variables from .env file
load_dotenv()

# Access environment variables
bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
tg_chat_id = os.getenv("TELEGRAM_CHAT_ID")

try:
    with open("stream_data.json", "r") as read_file:
        data_read = json.load(read_file)
except FileNotFoundError:
    print("Previous data not found.")
    data_read = []


def get_stream_data(channel, username):
    url = "https://api.streamelements.com/kappa/v2/points/" + channel + "/" + username
    response = requests.get(url)
    return json.loads(response.text)


async def main(channel, username):
    dados = get_stream_data(channel, username)
    idx = next(
        (
            i
            for i, item in enumerate(data_read)
            if (
                item["channel"] == dados["channel"]
                and item["username"] == dados["username"]
            )
        ),
        None,
    )
    if idx == None:
        print("Sem histórico anterior")
        data_read.append(dados)
    else:
        if data_read[idx]["points"] == dados["points"]:
            msg = (
                "🛑 Famador parado! Pontos: "
                + str(dados["points"])
                + " | User: "
                + dados["username"]
                + " | Rank: "
                + str(dados["rank"])
            )
            print(msg)
            bot = telegram.Bot(bot_token)
            async with bot:
                await bot.send_message(text=msg, chat_id=tg_chat_id)
        data_read[idx] = dados
    with open("stream_data.json", "w") as write_file:
        json.dump(data_read, write_file, indent=4)


if __name__ == "__main__":
    if len(sys.argv) < 3:
        sys.exit("O script requer dois argumentos: codigo do streamer e username")
    asyncio.run(main(sys.argv[1], sys.argv[2]))
