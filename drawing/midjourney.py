from typing import List
import base64
import httpx
import requests
from graia.ariadne.message.element import Image

from constants import config
from .base import DrawingAPI

class Midjourney(DrawingAPI):

    def __init__(self):
        self.headers = {
            "Accept": "application/json",
            "Content-type": "application/json"
        }

    async def text_to_img(self, prompt):
        payload = {
            "action": "generate",
            'prompt': f'{config.midjourney.prompt_prefix}, {prompt}',
            "timeout": f'{config.midjourney.draw_timeout}',
        }

        for key, value in config.sdwebui.dict(exclude_none=True).items():
            if isinstance(value, bool):
                payload[key] = 'true' if value else 'false'
            else:
                payload[key] = value

        # url = "https://api.zhishuyun.com/midjourney/imagine?token=637b5071cfe5404b988facef28bb0de7"
        # response = requests.post(url, json=payload, headers=headers)

        resp = await httpx.AsyncClient(timeout=config.midjourney.timeout).post(f"{config.midjourney.api_url}?token={config.midjourney.token}",
                                                                            json=payload, headers=self.headers)
        print(resp.json())

        resp.raise_for_status()
        r = resp.json()

        return [Image(base64=i) for i in r.get('images', [])]

    # Todo:// 重写 img_to_img 方法，不过目前也用不到...
    async def img_to_img(self, init_images: List[Image], prompt=''):
        # 需要调用get_bytes方法，才能获取到base64字段内容
        for x in init_images: await x.get_bytes()
        # 消息链显示字符串中有“[图片]”字样，需要过滤
        prompt = prompt.replace("[图片]", "")
        payload = {
            'init_images': [x.base64 for x in init_images],
            'enable_hr': 'false',
            'denoising_strength': 0.45,
            'prompt': f'{config.sdwebui.prompt_prefix}, {prompt}',
            'steps': 15,
            'seed': -1,
            'batch_size': 1,
            'n_iter': 1,
            'cfg_scale': 7.5,
            'restore_faces': 'false',
            'tiling': 'false',
            'negative_prompt': config.sdwebui.negative_prompt,
            'eta': 0,
            'sampler_index': config.sdwebui.sampler_index,
            "filter_nsfw": 'true' if config.sdwebui.filter_nsfw else 'false',
        }

        for key, value in config.sdwebui.dict(exclude_none=True).items():
            if isinstance(value, bool):
                payload[key] = 'true' if value else 'false'
            else:
                payload[key] = value

        resp = await httpx.AsyncClient(timeout=config.sdwebui.timeout).post(f"{config.sdwebui.api_url}sdapi/v1/img2img",
                                                                            json=payload, headers=self.headers)
        resp.raise_for_status()
        r = resp.json()
        return [Image(base64=i) for i in r.get('images', [])]
