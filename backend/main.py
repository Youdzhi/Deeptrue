from tiktok_down import TikTokDownloader
import cv2
import os
from datetime import datetime
import glob
import requests
from dotenv import load_dotenv
from concurrent.futures import ThreadPoolExecutor, as_completed

userid = '1234567890'
user_path = userid + '_tt'

downloader = TikTokDownloader(save_path=user_path)

# Скачиваем видео
downloader.download_video("https://vt.tiktok.com/ZSyMN8Q28/")

# Ищем скачанный .mp4
video_files = glob.glob(os.path.join(user_path, "*.mp4"))
if not video_files:
    raise FileNotFoundError("Видео не найдено после загрузки")

video_path = video_files[0]

# Создаем папку для кадров
folder_name = f"tiktok_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
frames_folder = os.path.join(user_path, folder_name)
os.makedirs(frames_folder, exist_ok=True)

# Читаем видео
cap = cv2.VideoCapture(video_path)

frame_count = 0
saved_count = 0

while True:
    ret, frame = cap.read()
    if not ret:
        break

    # сохраняем каждый 10-й кадр
    if frame_count % 10 == 0:
        frame_file = os.path.join(frames_folder, f"frame_{saved_count:05d}.jpg")
        cv2.imwrite(frame_file, frame)
        saved_count += 1

    frame_count += 1

cap.release()

print(f"✅ Готово! Сохранено {saved_count} кадров в {frames_folder}")

# AI Generated Frame Checker
print("\n🔍 Начинаю проверку кадров на AI-генерацию...")

# Загружаем переменные окружения из .env
load_dotenv()
api_user = os.getenv('SIGHTENGINE_API_USER')
api_secret = os.getenv('SIGHTENGINE_API_SECRET')

if not api_user or not api_secret:
    raise ValueError("API ключи не найдены в .env файле. Убедитесь, что SIGHTENGINE_API_USER и SIGHTENGINE_API_SECRET установлены.")

# Находим все кадры
frame_files = sorted(glob.glob(os.path.join(frames_folder, "frame_*.jpg")))
total_frames = len(frame_files)

if total_frames == 0:
    print("⚠️ Кадры не найдены для проверки")
else:
    # Создаем пустой массив для результатов
    ai_generated_array = [None] * total_frames
    
    # Определяем, какие кадры проверить (максимум 10 API вызовов)
    max_api_calls = min(10, total_frames)
    step = max(1, total_frames // max_api_calls)
    
    # Выбираем индексы для проверки
    frames_to_check = []
    for i in range(0, total_frames, step):
        frames_to_check.append(i)
        if len(frames_to_check) >= max_api_calls:
            break
    
    # Если не набрали 10, добавляем последний кадр
    if len(frames_to_check) < max_api_calls and total_frames > 0:
        frames_to_check.append(total_frames - 1)
    
    # Функция для проверки одного кадра
    def check_frame_ai_generated(frame_index, frame_path):
        """Проверяет один кадр на AI-генерацию через Sightengine API"""
        try:
            with open(frame_path, 'rb') as f:
                files = {'media': f}
                data = {
                    'models': 'genai',
                    'api_user': api_user,
                    'api_secret': api_secret
                }
                response = requests.post('https://api.sightengine.com/1.0/check.json', files=files, data=data)
                response.raise_for_status()
                result = response.json()
                
                # Получаем процент AI-генерации (0-1, конвертируем в 0-100)
                ai_score = result.get('type', {}).get('ai_generated', 0.0)
                percentage = int(ai_score * 100)
                
                return frame_index, percentage
        except Exception as e:
            print(f"⚠️ Ошибка при проверке кадра {frame_index}: {e}")
            return frame_index, 50  # По умолчанию 50 при ошибке
    
    # Проверяем кадры параллельно
    results = []
    with ThreadPoolExecutor(max_workers=max_api_calls) as executor:
        futures = {
            executor.submit(check_frame_ai_generated, idx, frame_files[idx]): idx 
            for idx in frames_to_check
        }
        
        for future in as_completed(futures):
            frame_index, percentage = future.result()
            results.append((frame_index, percentage))
            print(f"📊 Кадр {frame_index}: {percentage}% AI-генерации")
    
    # Сортируем результаты по индексу
    results.sort(key=lambda x: x[0])
    
    # Применяем логику разметки
    for frame_index, percentage in results:
        if percentage >= 50:  # AI-генерация (>=50%)
            # Размечаем 100 кадров: 50 влево, 50 вправо
            start_idx = max(0, frame_index - 50)
            end_idx = min(total_frames, frame_index + 51)
            
            for idx in range(start_idx, end_idx):
                if ai_generated_array[idx] is None:
                    ai_generated_array[idx] = 100
                elif ai_generated_array[idx] == 0:
                    # Пересечение с non-AI меткой -> 50
                    ai_generated_array[idx] = 50
        else:  # Не AI-генерация (<50%)
            # Размечаем 40 кадров: 20 влево, 20 вправо
            start_idx = max(0, frame_index - 20)
            end_idx = min(total_frames, frame_index + 21)
            
            for idx in range(start_idx, end_idx):
                if ai_generated_array[idx] is None:
                    ai_generated_array[idx] = 0
                elif ai_generated_array[idx] == 100:
                    # Пересечение с AI меткой -> 50
                    ai_generated_array[idx] = 50
    
    # Заполняем оставшиеся None значения (если есть)
    # Используем ближайшее значение или 50 по умолчанию
    for i in range(total_frames):
        if ai_generated_array[i] is None:
            # Ищем ближайшее заполненное значение
            left_val = None
            right_val = None
            
            # Ищем слева
            for j in range(i - 1, -1, -1):
                if ai_generated_array[j] is not None:
                    left_val = ai_generated_array[j]
                    break
            
            # Ищем справа
            for j in range(i + 1, total_frames):
                if ai_generated_array[j] is not None:
                    right_val = ai_generated_array[j]
                    break
            
            # Используем ближайшее или 50
            if left_val is not None and right_val is not None:
                ai_generated_array[i] = (left_val + right_val) // 2
            elif left_val is not None:
                ai_generated_array[i] = left_val
            elif right_val is not None:
                ai_generated_array[i] = right_val
            else:
                ai_generated_array[i] = 50
    
    # Вычисляем среднее значение
    mean_value = sum(ai_generated_array) / len(ai_generated_array) if ai_generated_array else 0
    
    # Выводим результаты
    print(f"\n📈 Результаты проверки AI-генерации:")
    print(f"📊 Массив AI-генерации: {ai_generated_array}")
    print(f"📉 Среднее значение: {mean_value:.2f}%")
