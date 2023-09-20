import time
from rgbmatrix import RGBMatrix, RGBMatrixOptions
from render import create_time_image
from gettime import get_current_time

def main():
    options = RGBMatrixOptions()

    options.rows = 32
    options.cols = 64
    options.chain_length = 1
    options.parallel =1 

    matrix = RGBMatrix(options=options)

    try:
        while True:
            hour, minute = get_current_time()
            image = create_time_image((hour, minute))
            matrix.SetImage(image.convert('RGB'))
            time.sleep(60)

    except KeyboardInterrupt:
        matrix.Clear()

if __name__ == "__main__":
    main()
