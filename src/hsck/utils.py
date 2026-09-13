def get_page_dir(vod_id: int) -> str:
    return str((vod_id + 99) // 100)
