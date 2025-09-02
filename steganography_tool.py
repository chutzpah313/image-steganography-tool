import os
import cv2
import numpy as np
import base64

class SteganographyTool:
    def __init__(self):
        self.delimiter = "<<<END_OF_FILE>>>"

    def file_to_binary(self, file_path: str) -> str:
        try:
            with open(file_path, 'rb') as file:
                file_data = file.read()
            file_ext = os.path.splitext(file_path)[1]
            file_info = f"{file_ext}|||{base64.b64encode(file_data).decode('utf-8')}"
            binary_data = ''.join(format(ord(char), '08b') for char in file_info)
            delimiter_binary = ''.join(format(ord(char), '08b') for char in self.delimiter)
            return binary_data + delimiter_binary
        except Exception as e:
            raise Exception(f"Error reading file: {str(e)}")

    def binary_to_file(self, binary_data: str, output_path: str):
        try:
            text_data = ""
            for i in range(0, len(binary_data), 8):
                byte = binary_data[i:i+8]
                if len(byte) == 8:
                    text_data += chr(int(byte, 2))
            if self.delimiter in text_data:
                text_data = text_data.split(self.delimiter)[0]
            if "|||" in text_data:
                file_ext, encoded_data = text_data.split("|||", 1)
                file_data = base64.b64decode(encoded_data.encode('utf-8'))
                if not output_path.endswith(file_ext):
                    output_path += file_ext
                with open(output_path, 'wb') as file:
                    file.write(file_data)
                return output_path
            else:
                raise Exception("Invalid data format")
        except Exception as e:
            raise Exception(f"Error reconstructing file: {str(e)}")

    def hide_data_in_image(self, cover_image_path: str, secret_file_path: str, output_image_path: str):
        try:
            cover_image = cv2.imread(cover_image_path)
            if cover_image is None:
                raise Exception("Could not load cover image")
            binary_data = self.file_to_binary(secret_file_path)
            image_capacity = cover_image.shape[0] * cover_image.shape[1] * 3
            if len(binary_data) > image_capacity:
                raise Exception(f"Image too small. Need {len(binary_data)} bits, but image can hold {image_capacity} bits")
            flat_image = cover_image.flatten()
            for i, bit in enumerate(binary_data):
                flat_image[i] = (flat_image[i] & 0xFE) | int(bit)
            stego_image = flat_image.reshape(cover_image.shape)
            cv2.imwrite(output_image_path, stego_image)
            print(f"Successfully hid {os.path.basename(secret_file_path)} in {os.path.basename(cover_image_path)}")
            print(f"Stego image saved as: {output_image_path}")
            return output_image_path
        except Exception as e:
            raise Exception(f"Error hiding data: {str(e)}")

    def extract_data_from_image(self, stego_image_path: str, output_file_path: str):
        try:
            stego_image = cv2.imread(stego_image_path)
            if stego_image is None:
                raise Exception("Could not load stego image")
            flat_image = stego_image.flatten()
            binary_data = ""
            delimiter_binary = ''.join(format(ord(char), '08b') for char in self.delimiter)
            for pixel_value in flat_image:
                binary_data += str(pixel_value & 1)
                if binary_data.endswith(delimiter_binary):
                    binary_data = binary_data[:-len(delimiter_binary)]
                    break
            extracted_file_path = self.binary_to_file(binary_data, output_file_path)
            print(f"Successfully extracted data from {os.path.basename(stego_image_path)}")
            print(f"Extracted file saved as: {extracted_file_path}")
            return extracted_file_path
        except Exception as e:
            raise Exception(f"Error extracting data: {str(e)}")

    def analyze_images(self, original_path: str, stego_path: str):
        try:
            original = cv2.imread(original_path)
            stego = cv2.imread(stego_path)
            if original is None or stego is None:
                raise Exception("Could not load images for analysis")
            original_size = os.path.getsize(original_path)
            stego_size = os.path.getsize(stego_path)
            print("\n=== IMAGE ANALYSIS RESULTS ===")
            print(f"Original image size: {original_size:,} bytes ({original_size/1024:.2f} KB)")
            print(f"Stego image size: {stego_size:,} bytes ({stego_size/1024:.2f} KB)")
            print(f"Size difference: {stego_size - original_size:,} bytes")
            print(f"Size change: {((stego_size - original_size) / original_size * 100):+.2f}%")
            mse = np.mean((original.astype(float) - stego.astype(float)) ** 2)
            if mse == 0:
                psnr = float('inf')
            else:
                psnr = 20 * np.log10(255.0 / np.sqrt(mse))
            print(f"\nImage Quality Metrics:")
            print(f"MSE (Mean Squared Error): {mse:.4f}")
            print(f"PSNR (Peak Signal-to-Noise Ratio): {psnr:.2f} dB")
            if psnr > 30:
                print("Quality: Excellent (visually identical)")
            elif psnr > 20:
                print("Quality: Good (minimal visible difference)")
            else:
                print("Quality: Poor (visible differences)")
            return {
                'original_size': original_size,
                'stego_size': stego_size,
                'mse': mse,
                'psnr': psnr
            }
        except Exception as e:
            raise Exception(f"Error analyzing images: {str(e)}")
