import asyncio


async def print_loading(idx: int, loaing_text: str = 'Loading...'):
    # frames = ['⠋', '⠙', '⠹', '⠸', '⠼', '⠴', '⠦', '⠧', '⠇', '⠏'] # 100 ms
    # frames = ['🙈 ', '🙈 ', '🙉 ', '🙊 '] # 300 ms
    frames = ['🕛 ', '🕐 ', '🕑 ', '🕒 ', '🕓 ', '🕔 ', '🕕 ', '🕖 ', '🕗 ', '🕘 ', '🕙 ', '🕚 '] # 100 ms
    print(f'\r{frames[idx % len(frames)]} {loaing_text}', end='', flush=True)

    await asyncio.sleep(0.1)