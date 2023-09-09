
def draw_pixel(x, y, pixel_colors, color=(255, 255, 255)):
    pixel_colors[x][y] = color

def render_number(number, x_offset, y_offset, pixel_colors):


    numbers = {
        '0': [
            " XX ",
            "X  X",
            "X  X",
            "X  X",
            " XX "
        ],
        '1': [
            " X  ",
            "XX  ",
            " X  ",
            " X  ",
            "XXX "
        ],
        '2': [
            " XX ",
            "X  X",
            "  X ",
            " X  ",
            "XXXX"
        ],
        '3': [
            "XXX ",
            "   X",
            " XX ",
            "   X",
            "XXX "
        ],
        '4': [
            "X  X",
            "X  X",
            "XXXX",
            "   X",
            "   X"
        ],
        '5': [
            "XXXX",
            "X   ",
            "XXX ",
            "   X",
            "XXX "
        ],
        '6': [
            " XX ",
            "X   ",
            "XXX ",
            "X  X",
            " XX "
        ],
        '7': [
            "XXXX",
            "   X",
            "  X ",
            " X  ",
            "X   "
        ],
        '8': [
            " XX ",
            "X  X",
            " XX ",
            "X  X",
            " XX "
        ],
        '9': [
            " XX ",
            "X  X",
            " XXX",
            "   X",
            " XX "
        ]
    }


    for y, row in enumerate(numbers[str(number)]):
        for x, char in enumerate(row):
            if char == 'X':
                draw_pixel(x + x_offset, y + y_offset, pixel_colors)


def render_colon(x_offset, y_offset, pixel_colors):
    draw_pixel(x_offset, y_offset + 1, pixel_colors)  # top dot
    draw_pixel(x_offset, y_offset + 3, pixel_colors)  # bottom dot



def clear_region(x_start, x_end, y_start, y_end, pixel_colors):
    for x in range(x_start, x_end):
        for y in range(y_start, y_end):
            pixel_colors[x][y] = (0, 0, 0) #bg black 

def render_time(hour_str, minute_str, pixel_colors):
    x_margin = (64 - 19) // 2  # Center time
    y_margin = 2  # Small margin from top

    render_number(hour_str[0], x_margin, y_margin, pixel_colors)
    render_number(hour_str[1], x_margin + 5, y_margin, pixel_colors)
    render_colon(x_margin + 10, y_margin, pixel_colors)
    render_number(minute_str[0], x_margin + 12, y_margin, pixel_colors)
    render_number(minute_str[1], x_margin + 17, y_margin, pixel_colors)

