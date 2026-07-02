import cv2
import os
import sys

def main():
    print("=== Frame Interleaving (YouTube 60fps/2x Prank) ===")
    v1_path = 'Video1.mp4'
    v2_path = 'Video2.mp4'
    out_path = 'OutVideo.mp4'

    # 1. Поиск файлов
    if not os.path.exists(v1_path):
        print(f"Ошибка: Файл '{v1_path}' не найден в текущей директории.")
        input("Нажмите Enter для выхода...")
        sys.exit(1)
    if not os.path.exists(v2_path):
        print(f"Ошибка: Файл '{v2_path}' не найден в текущей директории.")
        input("Нажмите Enter для выхода...")
        sys.exit(1)

    cap1 = cv2.VideoCapture(v1_path)
    cap2 = cv2.VideoCapture(v2_path)

    if not cap1.isOpened() or not cap2.isOpened():
        print("Ошибка: Не удалось открыть видеофайлы. Убедитесь, что они не повреждены.")
        input("Нажмите Enter для выхода...")
        sys.exit(1)

    # 2. Проверка длительности (по количеству кадров)
    frames1 = int(cap1.get(cv2.CAP_PROP_FRAME_COUNT))
    frames2 = int(cap2.get(cv2.CAP_PROP_FRAME_COUNT))

    fps1 = cap1.get(cv2.CAP_PROP_FPS)
    fps2 = cap2.get(cv2.CAP_PROP_FPS)

    print(f"[{v1_path}] Кадров: {frames1} | FPS: {fps1:.2f}")
    print(f"[{v2_path}] Кадров: {frames2} | FPS: {fps2:.2f}")

    target_frames = min(frames1, frames2)

    if frames1 != frames2:
        print("\n[Внимание] Длительность видео (количество кадров) отличается!")
        while True:
            choice = input("Обрезать более длинное видео до длительности более короткого? (y/n): ").strip().lower()
            if choice == 'y':
                print(f"Видео будут обрезаны до {target_frames} кадров.")
                break
            elif choice == 'n':
                print("Операция отменена пользователем.")
                cap1.release()
                cap2.release()
                input("Нажмите Enter для выхода...")
                sys.exit(0)
            else:
                print("Пожалуйста, введите 'y' (да) или 'n' (нет).")

    # Получаем разрешение из первого видео
    width = int(cap1.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap1.get(cv2.CAP_PROP_FRAME_HEIGHT))
    
    # 3. Алгоритм обработки
    # Используем mp4v кодек, который по умолчанию встроен в OpenCV (базируется на встроенном ffmpeg)
    # Это позволяет избежать необходимости установки ffmpeg в систему пользователя.
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    
    # Попытка задать максимальное качество (зависит от версии OpenCV, поддерживается в новых версиях)
    try:
        params = [cv2.VIDEOWRITER_PROP_QUALITY, 100]
        out = cv2.VideoWriter(out_path, fourcc, 60.0, (width, height), params=params)
    except Exception:
        out = cv2.VideoWriter(out_path, fourcc, 60.0, (width, height))

    if not out.isOpened():
        print("Ошибка: Не удалось создать выходной файл. Проверьте права доступа.")
        sys.exit(1)

    print(f"\nНачинаем обработку... Разрешение: {width}x{height}, FPS выходного видео: 60.0")
    print("Создаем OutVideo.mp4...")

    for i in range(target_frames):
        ret1, frame1 = cap1.read()
        ret2, frame2 = cap2.read()

        if not ret1 or not ret2:
            print(f"\n[Предупреждение] Чтение прервалось на кадре {i}.")
            break
        
        # Если разрешение Video2 отличается от Video1, масштабируем его
        if frame2.shape[:2] != frame1.shape[:2]:
            frame2 = cv2.resize(frame2, (width, height), interpolation=cv2.INTER_AREA)

        # Кадры из Video1 становятся ЧЕТНЫМИ (индекс 0, 2, 4...) -> видны при 30fps
        out.write(frame1)
        
        # Кадры из Video2 становятся НЕЧЕТНЫМИ (индекс 1, 3, 5...)
        out.write(frame2)
        
        if (i + 1) % 100 == 0 or (i + 1) == target_frames:
            percent = ((i + 1) / target_frames) * 100
            print(f"\rПрогресс: {i + 1}/{target_frames} кадров ({percent:.1f}%)", end="")

    print("\n\nСохранение файла...")
    cap1.release()
    cap2.release()
    out.release()

    print(f"Успешно! Видео сохранено как '{out_path}'.")
    input("Нажмите Enter для выхода...")

if __name__ == "__main__":
    main()
