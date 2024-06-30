import random

import love_metod.postcard as postcard
import love_metod.text as text
import love_metod.sticker as sticker


async def return_compliment():
    return await random_compliment()


async def random_compliment():
    random_number = random.randint(0, 29)
    return text.var[random_number]


async def random_stickers():
    random_number = random.randint(0, 9)
    return sticker.sticker_id[random_number]


async def random_postcard():
    random_number = random.randint(0, 4)
    path = postcard.text_postcard_key[random_number]
    caption = postcard.text_postcard.get(postcard.text_postcard_key[random_number])
    return path, caption
