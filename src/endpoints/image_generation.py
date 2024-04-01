from openai import OpenAI
import requests
from io import BytesIO
from PIL import Image
import numpy as np
import os 
from typing import List
from uuid import uuid4
from src.game.configs import TEMP_IMAGE_DATA_PATH
from dotenv import load_dotenv

load_dotenv()

class Dalle:
    def __init__(
            self, 
            api_key:str=os.environ.get("OPENAI_API_KEY"),
            output_dir:str=TEMP_IMAGE_DATA_PATH,
            model:str="dall-e-3",
        ):
        self.api_key = api_key
        self.output_dir = output_dir
        self.client = OpenAI()
        self.model = model

    def crop_height(self, img, pixels):
        width, height = img.size
        half_pixels = pixels // 2
        # crop from top
        img = img.crop((0, half_pixels, width, height))
        # crop from bottom
        img = img.crop((0, 0, width, height - half_pixels))
        return img
    
    def scale_image(self, img, percent:float=0.1):
        width, height = img.size
        new_width = int(width * percent)
        new_height = int(height * percent)
        img = img.resize((new_width, new_height))
        return img

    def generate(
            self, 
            prompt:str, 
            size:str="1792x1024", 
            quality:str="standard", 
            n:int=1,
            scale:float=0.6,
        ):
        response = self.client.images.generate(
            prompt=prompt,
            size=size,
            quality=quality,
            model=self.model,
            n=n,
        )
        url = response.data[0].url
        img = requests.get(url)
        img = Image.open(BytesIO(img.content))
        img = self.scale_image(img, scale)
        return img
    
    def _prepare_image(self, image:np.ndarray|Image.Image):
        if isinstance(image, np.ndarray):
            image = Image.fromarray(image)
        image_path = self.output_dir+str(uuid4())+".png"
        image = image.convert("RGBA")
        image.save(image_path, "PNG")        
        return image_path
    
    def _prepare_images(self, images:List[np.ndarray|Image.Image]):
        # convert all to numpy arrays
        images = [np.array(image) if isinstance(image, Image.Image) else image for image in images]
        max_height = sum([image.shape[0] for image in images])
        total_width = max([image.shape[1] for image in images])
        # create a blank image
        new_image = np.zeros((max_height, total_width, 3), dtype=np.uint8)
        # fill the blank image with the images
        y_offset = 0
        for image in images:
            new_image[y_offset:y_offset+image.shape[0], :image.shape[1]] = image
            y_offset += image.shape[0]
        # convert the numpy array to an image
        image = Image.fromarray(new_image)
        # scale the image
        image = self.scale_image(image, 0.6)
        image_path = self.output_dir+str(uuid4())+".png"
        # convert to RGBA
        image = image.convert("RGBA")
        image.save(image_path, "PNG")
        return image_path

    
    def generate_from_image(
            self, 
            image:np.ndarray|Image.Image|List[np.ndarray|Image.Image], 
            prompt:str, 
            size:str="1024x1024", 
            n:int=1,
            scale:float=0.6,
        ):
        if isinstance(image, list):
            image_path = self._prepare_images(image)
        else:
            image_path = self._prepare_image(image)

        response = self.client.images.edit(
            image=open(image_path,"rb"),
            prompt=prompt,
            size=size,
        )

        os.remove(image_path)

        url = response.data[0].url
        img = requests.get(url)
        img = Image.open(BytesIO(img.content))
        img = self.scale_image(img, scale)
        return img
    
    def _generate_stage_art(
            self,
            prompt: str,
    ):
        return self.generate(prompt)
    
    def _generate_character_art(
            self,
            prompt:str,
            character_images: List[np.ndarray],
    ):
        prompt = "Use the images provided to create the scene described below. " + prompt
        # return self.generate_from_image(character_images, prompt)
        return self.generate(prompt)
        