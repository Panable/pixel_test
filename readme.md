## Nexel: A Python Version of the Tidbyt

# Overview

This project is a custom, Python version of the Tidbyt because I'm too cheap to buy one for myself (plus I thought it would be fun). Using a combination of Pillow, Python, RGBMatrix, and Numpy to render text and images.

# Hardware

This project is currently setup for a [Waveshare 64x32 Matrix](https://www.waveshare.com/rgb-matrix-p3-64x32.htm), a [Raspberry Pi Zero 2 WH](https://www.raspberrypi.com/products/raspberry-pi-zero-2-w/) with pre-soldered headers as I'm lazy and terrible at soldering, and an [Adafruit Bonnet](https://www.adafruit.com/product/3211) to make things easier. If you feel inclined, you could pinout the matrix to your Pi manually, but that's out of the scope of this document. More information re wiring can be found on [hzeller's repo](https://github.com/hzeller/rpi-rgb-led-matrix).


# How it works (software)

1. **Matrix Initialization**: First, we setup LED Matrix with desired configuration. I'm currently just using a single 64x32 matrix display, but there's nothing stopping you chaining multiple together if you wanted.

```
options = RGBMatrixOptions()
options.rows = 32
options.cols = 64
options.chain_length = 1
options.parallel = 1
matrix = RGBMatrix(options = options)
```

2. **Calculating Text Dimensions with Pillow**: Here we use Pillow library, and calculate the dimensions of the given string - thanks to [Jose Fernando Costa's article on how this is done]("https://levelup.gitconnected.com/how-to-properly-calculate-text-size-in-pil-images-17a2cc6f51fd"). 

```
def get_text_dimensions(text_string, font):
    ascent, descent = font.getmetrics()
    text_width = font.getmask(text_string).getbbox()[2]
    text_height = font.getmask(text_string).getbbox()[3] + descent
    return (text_width, text_height)
```
2.1 **Rendering and Positioning**: After we get dimensions, we can move onto the part that renders the text. We create an image canvas with Pillow. Using the above dimensions, we calculate position to draw center (or wherever).

```
matrix_img = Image.new('RGB', (width, height), color=(0, 0, 0))
draw = ImageDraw.Draw(matrix_img)

x_position = (width - text_width) / 2
y_position = (height - text_height) / 2
draw.text((x_position, y_position)
```


2.2 **Numpy**: While this text would display fine on canvas, we need to actually fit and render properly on our matrix. So in order to do this, we convert our Pillow-created image to a numpy array, resize to matrix dimensions, and get it back into the correct format.

```
image_np = np.array(matrix_img)
image_np_resized(Image.fromarray(image_np).resize((width, height), Image.NEAREST))
```

# Actually getting the display to work with the Adafruit:

Overall, pretty easy once you've got the code setup. Just run
```
sudo python3 main.py --led-gpio-mapping=adafruit-hat
```


# Caveats:

There are a lot as I'm early into this. 

1. Firstly, I've not integrated the two (and more to come) functions into the display (i.e. it's currently main.py or main2.py depending on whatever you want to run). I'm going to figure out how I want to select what module to display at a later time once I'm happy with all the functionality and code.

2. There is a lot of cleanup that needs to be done in order to have this minimal. As we're running on a Pi Zero, we need to have as minimal of a setup as possible.

3. Flickering. Lots of it. The stocks render is currently flickering a bunch, and I'm yet to figure out the root cause. I'm sure it's obvious.

4. I haven't integrated (yet) a way to run the python without passing --led-gpio-mapping=adafruit-hat. I'm sure it's possible, but I haven't actually read the full documentation as I've mostly been debugging since the matrix arrived.


# Dependencies:

Currently, dependencies are:

1. Python3 & pip
2. Pillow library
3. rpi-rgb-led-matrix library (you can find a link to that where I talked about wiring/pinout).
4. Numpy.

