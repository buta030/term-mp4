import cv2
import time
import sys
import tkinter as tk
from tkinter import filedialog
import platform

# WindowsでANSIエスケープシーケンスを有効化するためのcolorama
try:
    import colorama
except ImportError:
    colorama = None

def rgb_fg(r, g, b):
    return f"\x1b[38;2;{r};{g};{b}m"

def rgb_bg(r, g, b):
    return f"\x1b[48;2;{r};{g};{b}m"

def frame_to_ascii_block(frame, width=130):
    height, original_width = frame.shape[:2]
    aspect_ratio = original_width / height
    char_height = int(width / aspect_ratio * 0.5)
    resized = cv2.resize(frame, (width, char_height * 2), interpolation=cv2.INTER_LINEAR)

    ascii_image_lines = []
    for y in range(0, resized.shape[0] - 1, 2):
        upper = resized[y]
        lower = resized[y + 1]
        line_chars = []
        for u_pixel, l_pixel in zip(upper, lower):
            b1, g1, r1 = u_pixel
            b2, g2, r2 = l_pixel
            fg = rgb_fg(r1, g1, b1)
            bg = rgb_bg(r2, g2, b2)
            line_chars.append(fg + bg + "▀")
        line_chars.append("\x1b[0m")
        ascii_image_lines.append("".join(line_chars))
    return "\n".join(ascii_image_lines)

def play_ascii_video(video_path, width=110):
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        print("動画を開けません。")
        return

    print("\x1b[2J")  # 画面クリア

    try:
        while cap.isOpened():
            start_time = time.perf_counter()

            ret, frame = cap.read()
            if not ret:
                break

            ascii_frame = frame_to_ascii_block(frame, width)
            sys.stdout.write("\x1b[H" + ascii_frame)
            sys.stdout.flush()

            elapsed = time.perf_counter() - start_time
            delay = max(0, (1/30) - elapsed)
            time.sleep(delay)

    finally:
        cap.release()

if __name__ == "__main__":
    # Windowsならcolorama初期化（ANSIエスケープ対応）
    if platform.system() == "Windows":
        if colorama is None:
            print("Windowsでのカラー表示にはcoloramaライブラリが必要です。")
            print("次のコマンドでインストールしてください：")
            print("pip install colorama")
            sys.exit(1)
        else:
            colorama.init()

    # Tkinterのrootウィンドウを非表示で作成
    root = tk.Tk()
    root.withdraw()

    # ファイル選択ダイアログ
    video_file = filedialog.askopenfilename(
        title="動画ファイルを選択してください",
        filetypes=[("動画ファイル", "*.mp4 *.avi *.mov *.mkv"), ("すべてのファイル", "*.*")]
    )

    if not video_file:
        print("ファイルが選択されませんでした。終了します。")
        sys.exit()

    play_ascii_video(video_file, width=110)
