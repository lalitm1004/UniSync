def progress_bar(title: str, progress: int, total: int) -> None:
    percent = 100 * (progress / float(total))
    bar = "█" * int(percent) + "-" * int(100 - percent)
    end = "\r" if progress != total else "\n"
    print(f"\r[{title}] |{bar}| {percent:.2f}%", end=end)