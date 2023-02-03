"""use python3.11 main.py to start """

import traceback

import tcod

import settings
import color
import exceptions
import input_handlers
import setup_game


def save_game(handler: input_handlers.BaseEventHandler, filename: str) -> None:
	""" if the current event handler has an active Engine then save it. """
	if isinstance(handler, input_handlers.EventHandler):
		handler.engine.save_as(filename)
		print(settings.str_file_saved)


def load_customfont():
    """ Load a custon font. A is the index of the first custom tile inside the file """
    a = 256
 
    #The "y" is the row index, here we load the sixth row in the font file. Increase the "6" to load any new rows from the file
    for y in range(5,6):
        tcod.console_map_ascii_codes_to_font(a, 32, 0, y)
        a += 32



def main() -> None:
	
	""" Load settings from settings.py"""
	screen_width = settings.screen_width
	screen_height = settings.screen_height
	tile_file = settings.tile_file
	title = settings.title
	
	""" Load tileset """
	tileset = tcod.tileset.load_tilesheet(tile_file, 32, 8, tcod.tileset.CHARMAP_TCOD)
	
	#tcod.console_set_custom_font('./images/graphic_tiles_16x16.png', tcod.FONT_TYPE_GREYSCALE | tcod.FONT_LAYOUT_TCOD, 32, 10)
	#load_customfont()

	""" Setup first Input Handler """	
	handler: input_handlers.BaseEventHandler = setup_game.MainMenu()

	""" Setup game window """
	with tcod.context.new_terminal(
		screen_width,
		screen_height,
		tileset = tileset,
		title = title,
		vsync = True,
	) as context:
		root_console = tcod.Console(screen_width, screen_height, order="F")

		try:
			while True:
				root_console.clear()
				handler.on_render(console=root_console)
				context.present(root_console)
			
				try:
					for event in tcod.event.wait():
						context.convert_event(event)
						handler = handler.handle_events(event)
				except Exception:	# Handle exceptions in game.
					traceback.print_exc()	# Print error to stderr.
					# Then print the error to the message log.
					if isinstance(handler, input_handlers.EventHandler):
						handler.engine.message_log.add_message(
							traceback.format_exc(), color.error
						)
		except exceptions.QuitWithoutSaving:
			raise
		except SystemExit:	# Save and Quit
			save_game(handler, settings.save_file)
			raise
		except BaseException:	# Save on any other unexpected exception.
			save_game(handler, settings.save_file)
			raise

			
if __name__ == "__main__":
	main()

