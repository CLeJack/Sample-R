extends Container

# Called when the node enters the scene tree for the first time.
func _ready() -> void:
	
	size_flags_horizontal = Control.SIZE_EXPAND_FILL
	var vspacing = size.y/3
	var cs = get_children()
	
	for c in cs:
		if(c is Button):
			c.custom_minimum_size = Vector2(50, 50)
			add_theme_constant_override("separation", vspacing - c.size.y)

	print("in main menu")


# Called every frame. 'delta' is the elapsed time since the previous frame.
func _process(delta: float) -> void:
	pass
