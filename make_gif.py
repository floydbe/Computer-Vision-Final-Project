from scitools.std import movie

def make_gif(frame_loc, frames_per_sec=1, output_file_loc="my_gif.gif"):
	movie(frame_loc + "/*.jpg", fps=frames_per_sec, output_file=output_file_loc)

make_gif("frames", 2)
