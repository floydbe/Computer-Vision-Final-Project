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

def Match(v, start_frame, end_frame, max_span = None):
	matches = []

	# if max_span was not user-supplied,
	# set it to the length of v to make
	# calculation below simpler.
	if max_span == None:
		max_span = len(v)

	for f,i in v.sub_iter(start_frame):
		if i > end_frame:
			break
		for g,j in v.sub_iter(i):
			distance = 0.0
			# if we are calculating a distance that is longer than the
			# max_span, move on.
			if (j-i) >= max_span:
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
	[-l, --length <maximum loop length> ]
	[-o, --optimize [edge, scale, all] ]
	[-t, --threshold <threshold> (only applicable in combination with -o)]
	<input video filename> <output animated gif filename>""" % myname)

if __name__== "__main__":
	start_frame = 0
	end_frame = None
	max_length = None
	video = None
	input_filename = None
	output_filename = None
	threshold = 0.20
	do_edge_match_optimization = False
	do_scale_match_optimization = False

	try:
		opts, args = getopt.getopt(sys.argv[1:], "s:e:o:t:l:", ["start=", "end=", "optimize=", "threshold=", "length="])

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
			elif o == "l" or o == "length":
				max_length = int(a)
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
			print("%s=%s" % (o,a))
	except getopt.GetoptError as error:
		usage(sys.argv[0])
		sys.exit(1)

	video = Video(filename)
	video = GrayVideo(video)
	if end_frame == None:
		end_frame = len(video)

	# matches is a list of tuples: (start frame, end frame, distance)
	matches = []
	if do_edge_match_optimization and not do_scale_match_optimization:
		# Edge optimization but no scale optimization
		edge_video = EdgeVideo(video)
		edge_matches = Match(edge_video, start_frame, end_frame, max_length)
		edge_matches = sorted(edge_matches, key=itemgetter(2))
		# compute full matches for good edge matches
		for a,b,distance in edge_matches:
			if distance < threshold:
				matches.append((a,b,d(video[a],video[b],video.norms[a],video.norms[b])))
	elif do_scale_match_optimization and not do_edge_match_optimization:
		# Scale optimization but no edge optimization
		scale_video = ScaleVideo(video)
		scale_matches = Match(scale_video, start_frame, end_frame, max_length)
		scale_matches = sorted(scale_matches, key=itemgetter(2))
		# compute full matches for good scale matches
		for a,b,distance in scale_matches:
			if distance < threshold:
				matches.append((a,b,d(video[a],video[b],video.norms[a],video.norms[b])))
	elif do_scale_match_optimization and do_edge_match_optimization:
		# Both optimizations
		edge_video = EdgeVideo(video)
		scale_video = ScaleVideo(edge_video)
		scale_matches = Match(scale_video, start_frame, end_frame, max_length)
		scale_matches = sorted(scale_matches, key=itemgetter(2))
		# compute full matches for good scale matches
		for a,b,distance in scale_matches:
			if distance < threshold:
				matches.append((a,b,d(video[a],video[b],video.norms[a],video.norms[b])))
	else:
		matches = Match(video, start_frame, end_frame, max_length)

	# Sort the matches according to their distance values
	# which is the 2th index of items in matches.
	matches = sorted(matches, key=itemgetter(2))

	# make matches a minimum distance of three frames.
	matches = [ match for match in matches if match[1]-match[0] >= 9 ]

	# print matches in csv style.
	Debug.Print("Results: \n")
	for match in matches:
		Debug.Print("%d,%d,%f" % (match[0], match[1], match[2]))
	if len(matches):
		Debug.Print("Generating %s ..." % output_filename)
		video[matches[0][0]:matches[0][1]].to_animated_gif(output_filename)
	else:
		print("Error: No matches!")
