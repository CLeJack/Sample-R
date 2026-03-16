extends Container

# Called when the node enters the scene tree for the first time.
var button_height: int = 50
func _ready() -> void:
	
	size_flags_horizontal = Control.SIZE_EXPAND_FILL
	var cs = get_children()
	for c in cs:
		if(c is Button):
			c.custom_minimum_size = Vector2(50, button_height)

	print("in main menu")


# Called every frame. 'delta' is the elapsed time since the previous frame.
func _process(delta: float) -> void:
	pass
