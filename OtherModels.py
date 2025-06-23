import torch
import whisper
import os
from diffusers import LTXConditionPipeline, LTXLatentUpsamplePipeline
from diffusers.pipelines.ltx.pipeline_ltx_condition import LTXVideoCondition
from diffusers.utils import export_to_video, load_image, load_video
from databaser import Databaser

def round_to_nearest_resolution_acceptable_by_vae(pipe, height, width):
    height = height - (height % pipe.vae_spatial_compression_ratio)
    width = width - (width % pipe.vae_spatial_compression_ratio)
    return height, width


class ImageToVideo:
    """Сначала загрузи модель, не забудь, сука"""
    def __init__(self,
                 image_path: str, prompt: str,
                 negative_prompt: str,
                 expected_height: int,
                 expected_width: int,
                 number_of_frames: int = 96,
                 downscale_factor: float = 2 / 3):

        self.__pipe = LTXConditionPipeline.from_pretrained(
            "Lightricks/LTX-Video-0.9.7-dev", torch_dtype=torch.bfloat16)
        self.__pipe_upsample = LTXLatentUpsamplePipeline.from_pretrained(
            "Lightricks/ltxv-spatial-upscaler-0.9.7",
            vae=self.__pipe.vae, torch_dtype=torch.bfloat16)
        self.__pipe.to("cuda")
        self.__pipe_upsample.to("cuda")
        self.__pipe.vae.enable_tiling()

        self.image = load_image(image_path)
        self.video = load_video(export_to_video([self.image]))
        self.condition1 = LTXVideoCondition(video=self.video, frame_index=0)

        self.prompt = prompt
        self.negative_prompt = negative_prompt  # For example "worst quality, inconsistent motion, blurry, jittery, distorted"
        self.expected_height, self.expected_width = expected_height, expected_width
        self.downscale_factor = downscale_factor
        self.number_of_frames = number_of_frames

    def update_parameters_with_image(self,
                        image_path: str, prompt: str,
                        negative_prompt: str,
                        expected_height: int,
                        expected_width: int,
                        number_of_frames: int = 96,
                        downscale_factor: float = 2/3):

        self.image = load_image(image_path)
        self.video = load_video(export_to_video([self.image])) # compress the image using video compression as the model was trained on videos
        self.condition1 = LTXVideoCondition(video=self.video, frame_index=0)

        self.prompt = prompt
        self.negative_prompt = negative_prompt# For example "worst quality, inconsistent motion, blurry, jittery, distorted"
        self.expected_height, self.expected_width = expected_height, expected_width
        self.downscale_factor = downscale_factor
        self.number_of_frames = number_of_frames

    def generate_video_from_image(self, output_path):
        # Part 1. Generate video at smaller resolution
        downscaled_height = int(self.expected_height * self.downscale_factor)
        downscaled_width = int(self.expected_width * self.downscale_factor)
        downscaled_height, downscaled_width = round_to_nearest_resolution_acceptable_by_vae(
            self.__pipe,
            downscaled_height,
            downscaled_width)

        latents = self.__pipe(
            conditions=[self.condition1],
            prompt=self.prompt,
            negative_prompt=self.negative_prompt,
            width=downscaled_width,
            height=downscaled_height,
            num_frames=self.number_of_frames,
            num_inference_steps=30,
            generator=torch.Generator().manual_seed(0),
            output_type="latent",
        ).frames

        # Part 2. Upscale generated video using latent upsampler with fewer inference steps
        # The available latent upsampler upscales the height/width by 2x
        upscaled_height = downscaled_height * 2
        upscaled_width = downscaled_width * 2
        upscaled_latents = self.__pipe_upsample(
            latents=latents,
            output_type="latent"
        ).frames

        # Part 3. Denoise the upscaled video with few steps to improve texture (optional, but recommended)
        self.video = self.__pipe(
            conditions=[self.condition1],
            prompt=self.prompt,
            negative_prompt=self.negative_prompt,
            width=upscaled_width,
            height=upscaled_height,
            num_frames=self.number_of_frames,
            denoise_strength=0.4,  # Effectively, 4 inference steps out of 10
            num_inference_steps=10,
            latents=upscaled_latents,
            decode_timestep=0.05,
            image_cond_noise_scale=0.025,
            generator=torch.Generator().manual_seed(0),
            output_type="pil",
        ).frames[0]

        # Part 4. Downscale the video to the expected resolution
        video = [frame.resize(self.expected_width,
                               self.expected_height) for frame in self.video]
        export_to_video(video, output_path, fps=24)


class AudioToText:
    def __init__(self):
        self.__model = whisper.load_model("turbo")
        self.db = Databaser()

    def transcribe(self, file_id: str):
        try:
            file = self.db.get_file(file_id)
            result = self.__model.transcribe(file['path'], fp16=False)

            save_dir = 'static/uploads'
            os.makedirs(save_dir, exist_ok=True)
            filename = file['name'] + '_tr'
            filepath = os.path.join(save_dir, filename).replace('\\', '/')

            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(result)
            f.close()

            self.db.add_transcribed_file(file['id'], filename, filepath)

        except Exception as err:
            return f"Error occurred: {err!r}"


class TextToSpeech:
    pass