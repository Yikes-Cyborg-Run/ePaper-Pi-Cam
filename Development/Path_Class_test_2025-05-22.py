from pathlib import Path

# home_dir=Path.home()

# print(home_dir)
#home_dir=Path(__file__).parent.resolve()
home_dir=Path.cwd()
font_dir=home_dir/"Fonts"
font_list=[]
for f in list(font_dir.glob('*ttf')):
    if Path(f).is_file():
        font_list.append(f)

print(home_dir)
