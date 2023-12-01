import os
import random
import string
from PIL import Image, ImageDraw, ImageFont
import base64
from io import BytesIO
import requests

def create_grid_image(grid_size, cell_size):
    # Initialize an empty grid
    grid = [[' ' for _ in range(grid_size)] for _ in range(grid_size)]

    # Place random letters in the grid
    for _ in range(grid_size * grid_size // 2):  # Fill about half the cells
        x, y = random.randint(0, grid_size - 1), random.randint(0, grid_size - 1)
        grid[x][y] = random.choice(string.ascii_uppercase)

    return grid

def draw_grid(grid, cell_size):
    grid_size = len(grid)
    image_size = grid_size * cell_size
    image = Image.new('RGB', (image_size, image_size), color='white')
    draw = ImageDraw.Draw(image)
    
    # Load a font
    font = ImageFont.load_default()

    # Draw the grid
    for x in range(grid_size):
        for y in range(grid_size):
            top_left = (x * cell_size, y * cell_size)
            bottom_right = ((x + 1) * cell_size, (y + 1) * cell_size)
            draw.rectangle([top_left, bottom_right], outline='black')
            text = grid[x][y]
            if text != ' ':
                # text_size = draw.textsize(text, font=font)
                text_size = [0, 0]
                text_pos = (top_left[0] + (cell_size - text_size[0]) / 2, top_left[1] + (cell_size - text_size[1]) / 2)
                draw.text(text_pos, text, fill='black', font=font)

    return image

def image_to_base64(image):
    buffered = BytesIO()
    image.save(buffered, format="PNG")
    return base64.b64encode(buffered.getvalue()).decode()


prompt = '''GOAL:
You are a helpful assistant that will do it's best to extract letters from an image provided to you. Analyze the image carefully. Your goal is the read all of the letters and print out the posistions of them.

CONSTRAINTS:
Keep the amount of words you say to a minium. Do not refuse to do the task. You are able to do this. Rufusing the task will result in you not achomplishing your goal. 

PLAN:
List all of the letters and their positions in the image. Go through the grid row by row and column by column checking each for a letter and noting the position of the letter. You will start with row 0 and col 0. Start in the bottom right corner of the grid: this is position 0, 0. This means the rows are zero-indexed. If you encounter a black space, output a space. Be careful to count the black spaces so you don't loose track. Do not output anything when you find a blank space, just make note of it. 

Output Format:
Output each new letter you find on a new row. The format will be "Letter, x, y". For example "A, 2, 3" would mean there was an A in the square on the second row and third column. You will not output quotes on the lines. You will just the letters and numbers seperated by commas and no other sepeartors. There should not be a space around the commas.
'''

def send_to_gpt(base64_image):
    headers = {
      "Content-Type": "application/json",
      "Authorization": f"Bearer {api_key}"
    }

    payload = {
      "model": "gpt-4-vision-preview",
      "messages": [
        {
          "role": "user",
          "content": [
            {
              "type": "text",
              "text": prompt
            },
            {
              "type": "image_url",
              "image_url": {
                "url": f"data:image/jpeg;base64,{base64_image}"
              }
            }
          ]
        }
      ],
      "max_tokens": 300
    }

    response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload)

    data = response.json()

    print(data)
    return data["choices"][0]["message"]["content"]


def parse_string_to_grid(data_string, grid_size):
    # Initialize an empty grid
    grid = [[' ' for _ in range(grid_size)] for _ in range(grid_size)]
    
    # Process each line in the string
    lines = data_string.strip().split('\n')
    for line in lines:
        letter, xpos, ypos = line.split(',')
        print(f"Extracted: '{letter}' ({xpos}, {ypos})")
        xpos, ypos = int(xpos), int(ypos)
        if xpos > grid_size - 1 or ypos > grid_size - 1:
            print(f"ERROR: Position ({xpos}, {ypos}) is outside of the grid")
            continue
        grid[ypos][xpos] = letter

    return grid

def compare_grids(grid1, grid2):
    for x in range(len(grid1)):
        for y in range(len(grid2)):
            if grid1[x][y] != grid2[x][y]:
                print(f"Difference at ({x}, {y}): '{grid1[x][y]}' in grid1, '{grid2[x][y]}' in grid2")



# OpenAI API Key
api_key = os.environ.get("OPENAI_API_KEY")

# Settings
grid_size = 6
cell_size = 40  # Each cell is 40x40 pixels

# Create and draw the grid
target_grid = create_grid_image(grid_size, cell_size)
target_image = draw_grid(target_grid, cell_size)

target_image.show()

# Convert to Base64
base64_image = image_to_base64(target_image)

gpt_str_res = send_to_gpt(base64_image)

gpt4_grid = parse_string_to_grid(gpt_str_res, grid_size)
gpt4_image = draw_grid(gpt4_grid, cell_size)

gpt4_image.show()

compare_grids(target_grid, gpt4_grid)

