import keyboard
import requests
import wikipedia
import googletrans
import random
import tkinter as tk
import webbrowser
import torch
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import speech_recognition as sr
import sounddevice as sd
import pyttsx3
import time
import openai
import subprocess
from telethon.sync import TelegramClient
from telethon.errors import SessionPasswordNeededError
from telethon.tl.functions.messages import SearchRequest
from telethon.tl.types import InputMessagesFilterEmpty
from telethon.tl.types import InputPeerUser
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By

device = torch.device('cpu')
language = 'ru'
model_id = 'ru_v3'
sample_rate = 48000 # 48000
speaker = 'xenia' # Голоса aidar, baya, kseniya, xenia, random
put_accent = True
put_yo = True

model, example_text = torch.hub.load(repo_or_dir='snakers4/silero-models',
                                     model='silero_tts',
                                     language='ru',
                                     speaker='ru_v3')
model.to(device)

def speak(text):
    audio = model.apply_tts(text=text,
                            speaker=speaker,
                            sample_rate=sample_rate,
                            put_accent=put_accent,
                            put_yo=put_yo)

    sd.play(audio, sample_rate * 1.05)
    time.sleep((len(audio) / sample_rate)*1.15)
    sd.stop()

# sd.play(audio, sample_rate)
# time.sleep(len(audio) / sample_rate)
# sd.stop()

engine = pyttsx3.init()


def recognize_speech(language="ru"):
    r = sr.Recognizer()
    with sr.Microphone() as source:
        print("Скажите что-нибудь...")
        audio = r.listen(source)
    try:
        text = r.recognize_google(audio, language=language)
        print(f"Вы сказали: {text}")
        return text
    except sr.UnknownValueError:
        print("Не удалось распознать речь")
        return ""
    except sr.RequestError as e:
        print(f"Ошибка при запросе к серверу распознавания речи: {e}")
        return ""

def play_greetings():
    greetings = ["Привет!", "Здравствуйте!", "Доброе утро!", "Хэй!", "Добрый человек, здравствуй", "Нихау ма?", "Хелло"]
    greeting = random.choice(greetings)
    speak(greeting)

def play_farewell_and_quit():
    farewells = ["До свидания!", "Бай!", "Увидимся позже!", "Пока!","Хорошего дня"]
    farewell = random.choice(farewells)
    speak(farewell)
    exit()

def search_for_term_on_google():
    speak("Что вы хотите найти?")
    term = recognize_speech()
    if term:
        url = "https://www.google.com/search?q=" + term
        webbrowser.get().open(url)
        speak("Вот результаты поиска " + term)



def create_gui():
    root = tk.Tk()
    root.title("Voice Assistant")
    root.geometry("500x400")
    root.configure(background="#f2f2f2")

    greet_group = tk.LabelFrame(root, text="Приветствие")
    greet_group.pack(pady=10)

    greetings_button = tk.Button(greet_group, text="Произнести приветствие", width=25, command=play_greetings)
    greetings_button.pack(pady=5)

    farewell_group = tk.LabelFrame(root, text="Прощание")
    farewell_group.pack(pady=10)

    farewell_button = tk.Button(farewell_group, text="Произнести прощание и выйти", width=25, command=play_farewell_and_quit)
    farewell_button.pack(pady=5)

    search_group = tk.LabelFrame(root, text="Поиск")
    search_group.pack(pady=10)

    google_button = tk.Button(search_group, text="Поиск в Google", width=25, command=search_for_term_on_google)
    google_button.pack(pady=5)

    youtube_button = tk.Button(search_group, text="Поиск видео на YouTube", width=25, command=search_for_video_on_youtube)
    youtube_button.pack(pady=5)

    wikipedia_button = tk.Button(search_group, text="Поиск на Википедии", width=25, command=search_for_definition_on_wikipedia)
    wikipedia_button.pack(pady=5)

    translation_group = tk.LabelFrame(root, text="Перевод")
    translation_group.pack(pady=10)

    ask_group = tk.LabelFrame(root, text="Вопрос")
    ask_group.pack(pady=10)

    ask_button = tk.Button(ask_group, text="Вопрос", width=25, command=ask_gpt3)
    ask_button.pack(pady=5)

    translation_button = tk.Button(translation_group, text="Перевести текст", width=25, command=get_translation)
    translation_button.pack(pady=5)

    lang_button = tk.Button(translation_group, text="Выбрать язык", width=25, command=change_language)
    lang_button.pack(pady=5)


    weather_group = tk.LabelFrame(root, text="Погода")
    weather_group.pack(pady=10)

    weather_button = tk.Button(weather_group, text="Узнать погоду", width=25, command=get_weather_forecast)
    weather_button.pack(pady=5)
    root.mainloop()

def search_for_video_on_youtube():
    speak("Какое видео вы хотите найти??")
    video_query = recognize_speech()

    if video_query:
        url = "https://www.youtube.com/results?search_query=" + video_query
        speak("Вот результаты поиска" + video_query)

        current_video_index = 0
        should_respond = True  # Flag to control the assistant's responses

        # Set up the Chrome WebDriver. You can download it from https://sites.google.com/chromium.org/driver/
        driver = webdriver.Chrome()
        driver.get(url)

        while True:
            if should_respond:
                speak("Выберите действие: 'дальше', 'назад', 'выход', или 'воспроизвести'")
            choice = recognize_speech().lower()
            if choice == "дальше":
                current_video_index += 1
            elif choice == "назад":
                current_video_index = max(0, current_video_index - 1)
            elif choice == "выход":
                speak("Выход из режима просмотра видео.")
                driver.quit()
                break
            elif choice == "воспроизвести":
                try:
                    # Click on the selected video
                    video_elements = driver.find_elements(By.CSS_SELECTOR, "a#video-title")
                    if 0 <= current_video_index < len(video_elements):
                        video_elements[current_video_index].click()
                        should_respond = False
                except Exception as e:
                    print(f"An error occurred: {e}")
            elif choice == "зову":
                should_respond = True
            else:
                speak("Извините, не удалось распознать ваш выбор.")
                continue


def search_for_definition_on_wikipedia():
    speak("Что вы хотите знать?")
    definition = recognize_speech()
    if definition:
        wikipedia.set_lang(language)
        try:
            page = wikipedia.page(definition)
            speak(page.summary)
        except wikipedia.exceptions.DisambiguationError as e:
            speak("Не могли бы вы выразиться более конкретно? Есть несколько страниц с таким названием.")
        except wikipedia.exceptions.PageError as e:
            speak("Извините, я не смогла найти страницу с таким названием.")
        except:
            speak("Извините, что-то пошло не так.")

def get_translation():
    speak("Что вы хотите перевести?")
    text = recognize_speech()
    if text:
        translator = googletrans.Translator()
        translation = translator.translate(text, dest=language).text
        speak(" Текст" + text + " перевод " + translation)


def speak_en(text):
    device = torch.device('cpu')
    language_e = 'en'
    model_id_e = 'en_v3'
    sample_rate_e = 48000  # 48000
    speaker_e = 'xenia'  # Голоса aidar, baya, kseniya, xenia, random
    put_accent_e = True
    put_yo_e = True

    model, example_text = torch.hub.load(repo_or_dir='snakers4/silero-models',
                                         model='silero_tts',
                                         language=language_e,
                                         speaker=model_id_e)
    model.to(device)
    audio = model.apply_tts(text=text,
                            speaker=speaker_e,
                            sample_rate=sample_rate_e,
                            put_accent=put_accent_e,
                            put_yo=put_yo_e)

    sd.play(audio, sample_rate * 1.05)
    time.sleep((len(audio) / sample_rate) * 1.15)
    sd.stop()

def change_language():
    global language
    speak("Какой язык ты хочешь использовать?")
    new_language = recognize_speech()

    if new_language == "английский" or new_language == "English":
        try:

            language = googletrans.LANGUAGES["en"]
            speak(f"Language {new_language}")
            speak_en("Hello")
        except KeyError:
            speak("Sorry, I don't found this language. Try again.")

def get_weather_forecast():
    speak("Погоду в каком городе вы хотите знать?")
    city = recognize_speech()
    if city:
        url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid=<YOUR_API_KEY>&units=metric"
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            description = data['weather'][0]['description']
            temperature = data['main']['temp']
            humidity = data['main']['humidity']
            wind_speed = data['wind']['speed']
            speak(f"Погода в  {city} из {description}, с температурой  {temperature} Цельсия,влажность в процентах {humidity} и скорость ветра в метрах {wind_speed} в секунду.")
        else:
            speak("Извините, не удалось получить информацию о погоде для этого города.")
def pov():
    text = recognize_speech()
    speak(text)

def name():
    speak("Да, чем могу помочь?")

def run_person_through_social_nets_databases():
    speak("Какого человека ты хочешь найти?")
    person_name = recognize_speech()
    if person_name:
        url = f"https://pipl.ir/v1/?name={person_name}&key=<YOUR_API_KEY>"
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            if data['person'] and data['person']['names']:
                names = ", ".join(name for name in data['person']['names'])
                speak(f"Вот человек : {names}")
            else:
                speak("Извини я не нашел человека.")
        else:
            speak("Извините, годе произошла ошибка")

def stop_speaking():
    pyttsx3.init().stop()

keyboard.add_hotkey('esc', stop_speaking)
def ask_gpt3():
    API_KEY = "Your api key"
    openai.api_key = API_KEY

    speak("Какие вопросы вы хотите задать?")
    question = recognize_speech()
    speak("Дай мне несколько минут на раздумия")

    response = openai.Completion.create(
        engine="davinci",
        prompt=f"Question: {question}\nAnswer:",
        temperature=0.5,
        max_tokens=1024,
        n=1,
        stop=".",
        timeout=10,
    )

    answer = response.choices[0].text.strip()
    return answer
def poem():
    speak("Скажи, какое стихотворение ты хочешь создать?")
    stix = recognize_speech()
    speak("Сейчас создам произведение исскуства")
    openai.api_key = "Your api key"
    model_engine = "text-davinci-002"
    completions = openai.Completion.create(
        engine=model_engine,
        prompt=stix,
        max_tokens=1024,
        n=1,
        stop=None,
        temperature=random.uniform(0.5, 1),
    )
    poem = completions.choices[0].text
    return poem
def toss_coin():
    result = random.choice(["Орел", "Решка"])
    speak(f"Монетка {result}.")
def hay():
    greetings = ["Отлично, вы как !", "Хорошое, вы как !", "Нормально, у вас?!", "Гуд, энд йоу !", "Шикарно, у вас?"]
    greeting = random.choice(greetings)
    speak(greeting)
    h = recognize_speech()
    if h == "Все нормально" or h == "Хорошо":
        speak("Я очень рада за вас")
    elif h == "плохо":
        speak("Что у вас произошло?")
        h = recognize_speech()
        if h == "Мне скучно":
            speak("Можете по программировать или почитать книги")
        else:
            speak("За плохим всегда идет что-то хорошие, не огорчайтесь")
    else:
        speak("Все будет очень хорошо, потому что жизнь как инь и янь. Если есть что-то плохое, то есть что-то хорошие")
def open_telegram():
    path ="...Telegram.exe"
    subprocess.Popen(path)
def telegram():
    phone_number = "+Your phone"
    api_id = Your api id
    api_hash = "Your api hash"
    client = TelegramClient('my_session', api_id, api_hash)
    client.start()

    if not client.is_user_authorized():
        try:
            client.send_code_request(phone_number)
            client.sign_in(phone_number, input('Введите код, отправленный на ваш номер: '))
        except SessionPasswordNeededError:
            client.sign_in(password=input('Введите пароль двухфакторной аутентификации: '))

    dialogs = client.get_dialogs()
    speak("Что вы хотите найти в Телеграм поиске?")
    search_query = recognize_speech()
    results = []
    for dialog in dialogs:
        if dialog.is_user:
            messages = client(SearchRequest(
                peer=dialog.entity,
                q=search_query,
                filter=InputMessagesFilterEmpty(),
                min_date=None,
                max_date=None,
                offset_id=0,
                add_offset=0,
                limit=10,
                max_id=0,
                min_id=0,
                hash=0))

            # добавляем результаты поиска в список
            try:
                if messages.total > 0:
                    chat_results = []
                    for msg in messages.messages:
                        chat_results.append(msg.message)
                    results.append((dialog.name, chat_results))
            except:
                speak("Произошла ошибка")

    client.disconnect()

    return results
def play_song():
    speak("Что за музыку включить?")
    song_name = recognize_speech()
    speak("Минуту!")
    client_id = "Your client id"
    client_secret = "Your client secret"
    client_credentials_manager = SpotifyClientCredentials(client_id=client_id, client_secret=client_secret)
    sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)
    result = sp.search(q=song_name, type='track')
    if result['tracks']['total'] > 0:
        track = result['tracks']['items'][0]
        uri = track['uri']
        sp.start_playback(uris=[uri])
    else:
        print("Извини, я не нашла данный трек .")

commands = {
    ("нави", "Нави"): name,
    ("hello", "hi", "Здравствуй", "Привет"): play_greetings,
    ("bye", "goodbye", "quit", "exit", "stop", "пока", "до свидания"): play_farewell_and_quit,
    ("search", "google", "find", "найди"): search_for_term_on_google,
    ("video", "youtube", "watch", "видео", "найди видео"): search_for_video_on_youtube,
    ("wikipedia", "definition", "about", "определение", "википедия"): search_for_definition_on_wikipedia,
    ("translate", "interpretation", "translation", "перевод", "перевести", "Переведи"): get_translation,
    ("language", "язык"): change_language,
    ("weather", "forecast", "погода", "прогноз"): get_weather_forecast,
    ("facebook", "person", "run", "пробей", "контакт"): run_person_through_social_nets_databases,
    ("toss", "coin", "монета", "подбрось"): toss_coin,
    ("Повтори за мной"):pov,
    # ("Что такое ", "У меня вопрос"): ask_gpt3,
    ("Музыка", "трек", "музыка"): play_song,
    ("графический интерфейс", "графика"): create_gui,
    ("Как дела", "Как ты", "Что нового"): hay,
    ("Стоп", "Оставновись", "Минуту", "минуту"): stop_speaking,
    # ("Телеграм", "Telegram", "телега"): telegram,
    ("Открой телегу"): open_telegram
}
def handle_input(input_text):

    for command, function in commands.items():
        if input_text in command:
            function()
            return
        # elif input_text == "Дай ответ":
        #     a = ask_gpt3()
        #     print(a)
        #     speak(a)
        #     break
        # elif input_text == "стихотворение":
        #     p = poem()
        #     print(p)
        #     speak(p)
        #     break
        elif input_text == "телега":
            p = telegram()
            speak(p)
        elif input_text == " ":
            speak("Вы ничего не сказали")
    speak("Извините, я не поняла эту команду")


while True:
    input_text = recognize_speech()
    handle_input(input_text)