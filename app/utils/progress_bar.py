def generate_progress_bar(progress: float) -> str:
    """Генерирует строку с прогресс-баром, используя цвета."""
    total_blocks = 10  # Длина шкалы прогресса
    filled_blocks = int(progress // 10)

    if progress < 30:
        color = "🟥"  # Красный (низкий прогресс)
    elif progress < 70:
        color = "🟨"  # Желтый (средний прогресс)
    else:
        color = "🟩"  # Зеленый (высокий прогресс)

    progress_bar = color * filled_blocks + "⬜" * (total_blocks - filled_blocks)
    return progress_bar