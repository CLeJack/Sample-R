from pathlib import Path

def load_gitignore(root_path: Path):
    """Parses .gitignore using modern Path objects."""
    # Start with standard defaults
    ignore_list = set(['.git', '__pycache__', '.vscode', '.idea', '.DS_Store'])
    gitignore_file = root_path / '.gitignore'
    
    if gitignore_file.exists():
        with gitignore_file.open('r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#'):
                    clean_line = line.replace('/', '').replace('\\', '')
                    ignore_list.add(clean_line)
    return ignore_list

def draw_tree(directory: Path, prefix: str = "", ignore_list: set = None):
    if ignore_list is None:
        ignore_list = set()

    try:
        # Sort to keep the output consistent
        items = sorted(list(directory.iterdir()), key=lambda x: x.name.lower())
    except PermissionError:
        return

    # Filter ignored items
    visible_items = [i for i in items if i.name not in ignore_list and i.suffix != ".wav"]
    
    for i, item in enumerate(visible_items):
        is_last = (i == len(visible_items) - 1)
        connector = "└── " if is_last else "├── "
        
        print(f"{prefix}{connector}{item.name}")
        
        if item.is_dir():
            new_prefix = prefix + ("    " if is_last else "│   ")
            draw_tree(item, new_prefix, ignore_list)

if __name__ == "__main__":
    # Path.cwd() gets the current working directory as an object
    root = Path.cwd()
    print(f"{root.name}/")
    ignores = load_gitignore(root)
    draw_tree(root, ignore_list=ignores)