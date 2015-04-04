#!/usr/bin/env python

from scitools.std import movie

def make_gif(frame_loc, frames_per_sec=1, output_file_loc="my_gif.gif"):
	movie(frame_loc + "/frame_*.jpg", fps=frames_per_sec, output_file=output_file_loc)

if __name__=="__main__":
	make_gif("frames", 2)
