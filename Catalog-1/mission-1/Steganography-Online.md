# Steganography Online: How It Works, Detection, Pros and Cons

## How it works

It uses **LSB (least significant bit) steganography** on PNG images. It runs entirely in the browser via JavaScript and the HTML canvas, so files are not uploaded to a server.

- **Encoding text:** You load a carrier image and type a message. The tool converts the message to bits and overwrites the lowest bit of the pixels' color channel values with them. Changing the last bit shifts a color value by at most 1 out of 255, which is invisible to the eye. You then download the result as a PNG.
- **Decoding:** You upload the PNG, and the tool reads the low bits back out and reassembles the message or image.

## Advantages

- No installation, and it works on any device with a browser
- Client-side processing, so your data stays on your machine
- Free and open source, so you can audit or self-host it
- Very simple, with no learning curve
- Lossless PNG output preserves the hidden data

## Disadvantages

- **No encryption or password.** Anyone who knows to decode it can read the message. Encrypt your text first if it matters.
- **Easy to detect.** Plain sequential LSB embedding is the most commonly analyzed method, and tools like zsteg catch it quickly.
- **Fragile.** Any lossy step (JPEG conversion, resizing, cropping, screenshots, or social media recompression) destroys the hidden data.
- **PNG only,** and the carrier needs to be large enough for the payload, so capacity is limited.
- **Not suitable for serious secrecy.** It's fine for learning, CTFs, watermark-style fun, or casual hiding, but not for anything where an adversary might analyze the file.
