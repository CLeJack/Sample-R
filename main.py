import dearpygui.dearpygui as dpg

import argparse


from sample_r.app import App

# --- CLI Argument Handling ---
def parse_args():
    parser = argparse.ArgumentParser(
        description="Sample-Resynthesis: Extracts and resynthesizes harmonics from WAV files.",
        epilog="Example: streamlit run app.py -- -i ./samples -o ./exports"
        )
    parser.add_argument("-i", "--input", default=".", help="Input directory")
    parser.add_argument("-o", "--output", default=".", help="Output directory")
    args, unknown = parser.parse_known_args()
    return args


if __name__ == "__main__":

    args = parse_args()
    # print(args, args.input, args.output)
    t = f'Beginning Sample-R\nInput Directory: {args.input}\nOutput Directory: {args.output}'
    dpg.create_context()

    
    dpg.create_viewport(title='Sample-R', width=App.WIDTH, height=App.HEIGHT)
    
    App.show(args.input, args.output, t)
    

    dpg.setup_dearpygui()
    dpg.show_viewport()
    # dpg.start_dearpygui()

    while dpg.is_dearpygui_running():
        # Insert your custom logic here (must be fast!)
        App.update()
        
        # Manually tell DPG to render the frame
        dpg.render_dearpygui_frame()

    dpg.destroy_context()
