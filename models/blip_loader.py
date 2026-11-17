from PIL import Image
import torch
from transformers import BlipProcessor, BlipForConditionalGeneration
from config.settings import BLIP_MODEL_NAME, DEVICE

class BLIPCaptioner:
    """Salesforce BLIP Image Captioning model wrapper."""

    def __init__(self, model_name: str = BLIP_MODEL_NAME):
        print(f"[INFO] Initializing BLIP Captioner ({model_name}) on {DEVICE}...")
        try:
            # Try loading from local cache first for instant initialization without network latency
            self.processor = BlipProcessor.from_pretrained(model_name, local_files_only=True)
            self.model = BlipForConditionalGeneration.from_pretrained(model_name, local_files_only=True)
        except Exception as e:
            print(f"[INFO] Local cache lookup skipped ({e}). Loading from hub...")
            self.processor = BlipProcessor.from_pretrained(model_name, local_files_only=False)
            self.model = BlipForConditionalGeneration.from_pretrained(model_name, local_files_only=False)

        self.device = torch.device(DEVICE)
        self.model.to(self.device)
        self.model.eval()
        print("[INFO] BLIP Captioner successfully loaded.")

    def generate_caption(self, image_input, prompt: str = None, max_new_tokens: int = 50) -> str:
        """
        Generates a descriptive natural language caption for an image.
        :param image_input: File path (str) or PIL Image instance.
        :param prompt: Optional text prompt for conditional captioning.
        :param max_new_tokens: Maximum tokens in generated caption.
        :return: Decoded string caption.
        """
        try:
            if isinstance(image_input, (str, bytes)):
                image = Image.open(image_input).convert("RGB")
            else:
                image = image_input.convert("RGB")

            if prompt:
                inputs = self.processor(images=image, text=prompt, return_tensors="pt").to(self.device)
            else:
                inputs = self.processor(images=image, return_tensors="pt").to(self.device)

            with torch.no_grad():
                out = self.model.generate(
                    **inputs,
                    max_new_tokens=max_new_tokens,
                    min_length=6,
                    num_beams=3
                )
            caption = self.processor.decode(out[0], skip_special_tokens=True).strip()
            return caption
        except Exception as e:
            print(f"[ERROR] Caption generation failed: {e}")
            return "Unable to generate caption for this image."
