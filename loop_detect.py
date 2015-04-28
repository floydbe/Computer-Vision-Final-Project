#!/usr/bin/env python

import cv2
import numpy as np
import Image
from video import Video, EdgeVideo, GrayVideo, ScaleVideo
from distance import d
import sys
import getopt
import re
from debug import Debug
from operator import itemgetter

def Match(v, start_frame, end_frame, min_span = 0, max_span = None):
	matches = []

	# if max_span was not user-supplied,
	# set it to the length of v to make
	# calculation below simpler.
	if max_span == None:
		max_span = len(v)

	for f,i in v.sub_iter(start_frame):
		if i > end_frame or (i + min_span) >= len(v):
			break
		for g,j in v.sub_iter(i + min_span):
			distance = 0.0
			# if we are calculating a distance that is longer than the
			# max_span, move on.
			if (j-i) > max_span:
				break
			# don't calculate the distance to ourselves.
			if i == j:
				continue
			distance = d(f,g,v.norms[i],v.norms[j])
			matches.append((i,j,distance))
			Debug.Print("d(%d,%d) = %f" % (i, j, distance))
	return matches

def usage(myname):
	print("""%s
[-s, --start <start frame>]
[-e, --end <end frame> ]
[-l, --min-length <minimum loop length (# for frames or #.#s for seconds)> ]
[-m, --max-length <minimum loop length (# for frames or #.#s for seconds)> ]
[-o, --optimize [edge, scale, all] ]
[-t, --threshold <threshold> (only applicable in combination with -o)]
[-i, --interactive]
<input video filename> <output animated gif filename>""" % myname)

if __name__== "__main__":
	start_frame = 0
	end_frame = None
	max_length = None
	min_length = 0
	video = None
	input_filename = None
	output_filename = None
	threshold = 0.20
	do_edge_match_optimization = False
	do_scale_match_optimization = False
	interactive_mode = False
	
	try:
		opts, args = getopt.getopt(sys.argv[1:], "s:e:o:t:l:m:i", ["start=", "end=", "optimize=", "threshold=", "min-length=", "max-length=", "interactive"])

		if len(args) != 2:
			raise getopt.GetoptError("Must specify input and output filenames as parameters.")
		input_filename = args[0]
		output_filename = args[1]

		for o, a in opts:
			o = re.sub("^-*", "", o)
			if o == "s" or o == "start":
				start_frame = int(a)
			elif o == "e" or o == "end":
				end_frame = int(a)
			elif o == "l" or o == "min-length":
				min_length = a
			elif o == "m" or o == "max-length":
				max_length = a
			elif o == "o" or o == "optimize":
				if a == "edge":
					do_edge_match_optimization = True
				if a == "scale":
					do_scale_match_optimization = True
				if a == "all":
					do_edge_match_optimization = True
					do_scale_match_optimization = True
			elif o == "t" or o == "threshold":
				threshold = float(a)
			elif o == "i" or o == "interactive":
				interactive_mode = True
			print("%s=%s" % (o,a))
	except getopt.GetoptError as error:
		usage(sys.argv[0])
		sys.exit(1)

	try:
		video = Video(input_filename)
		video = GrayVideo(video)
	except IOError as error:
		print("%s\n" % str(error))
		sys.exit(1)

	if end_frame == None:
		end_frame = len(video)

	# Convert length parameters with s variables to frames.
	try:
		if max_length != None:
			if str(max_length)[-1] == 's':
				max_length = int(float(max_length[:-1])*video.frames_per_second)
			else:
				max_length = int(max_length)
	except ValueError:
		print("Warning: Max length parameter is not valid. Using default.\n")
		max_length = None
	Debug.Print("max_length: %s\n" % str(max_length))

	try:
		if str(min_length)[-1] == 's':
			min_length = int(float(min_length[:-1])*video.frames_per_second)
		else:
			min_length = int(min_length)
	except ValueError:
		print("Warning: Min length parameter is not valid. Using default.\n")
		min_length = 0
	Debug.Print("min_length: %d\n" % min_length)

	# Sanitize user inputs
	if max_length != None and max_length < min_length:
		print("Max length cannot be shorter than min length.")
		usage(sys.argv[0])
		sys.exit(1)

	# matches is a list of tuples: (start frame, end frame, distance)
	matches = []
	if do_edge_match_optimization and not do_scale_match_optimization:
		# Edge optimization but no scale optimization
		edge_video = EdgeVideo(video)
		edge_matches = Match(edge_video,
			start_frame,
			end_frame,
			min_length,
			max_length)
		edge_matches = sorted(edge_matches, key=itemgetter(2))
		# compute full matches for good edge matches
		for a,b,distance in edge_matches:
			if distance < threshold:
				matches.append((a,b,d(video[a],video[b],video.norms[a],video.norms[b])))
	elif do_scale_match_optimization and not do_edge_match_optimization:
		# Scale optimization but no edge optimization
		scale_video = ScaleVideo(video)
		scale_matches = Match(scale_video,
			start_frame,
			end_frame,
			min_length,
			max_length)
		scale_matches = sorted(scale_matches, key=itemgetter(2))
		# compute full matches for good scale matches
		for a,b,distance in scale_matches:
			if distance < threshold:
				matches.append((a,b,d(video[a],video[b],video.norms[a],video.norms[b])))
	elif do_scale_match_optimization and do_edge_match_optimization:
		# Both optimizations
		edge_video = EdgeVideo(video)
		scale_video = ScaleVideo(edge_video)
		scale_matches = Match(scale_video,
			start_frame,
			end_frame,
			min_length,
			max_length)
		scale_matches = sorted(scale_matches, key=itemgetter(2))
		# compute full matches for good scale matches
		for a,b,distance in scale_matches:
			if distance < threshold:
				matches.append((a,b,d(video[a],video[b],video.norms[a],video.norms[b])))
	else:
		matches = Match(video, start_frame, end_frame, min_length, max_length)

	# Sort the matches according to their distance values
	# which is the 2th index of items in matches.
	matches = sorted(matches, key=itemgetter(2))

	# make matches a minimum distance
	matches = [ match for match in matches if match[1]-match[0] >= min_length ]

	# print matches in csv style.
	Debug.Print("Results: \n")
	for match in matches:
		Debug.Print("%d,%d,%f" % (match[0], match[1], match[2]))
	if len(matches):
		Debug.Print("Generating %s ..." % output_filename)
		
		if interactive_mode:
			for i in range(len(matches)):
				video[matches[i][0]:matches[i][1]].to_animated_gif(output_filename)
				usr_in = raw_input("Enter 'yes' to accept this result or 'no' to replace it with the next-best result: ")
				if usr_in == "yes":
					exit()
			print("No more results")
			exit()
		else:
			video[matches[0][0]:matches[0][1]].to_animated_gif(output_filename)
	else:
		print("Error: No matches!")
