#!/usr/bin/env python

import numpy as np
import Image

def d(im1, im2, im1Norm=0, im2Norm=0):
	i1_s = im1.shape
	i2_s = im2.shape
	assert (i1_s == i2_s), "frames do not have same dimentions"
	if (len(i1_s) == 2):
		total = 0
		for x in range(i1_s[0]):
			for y in range(i1_s[1]):
				product = im1[x][y] * im2[x][y]
				total += product
		existing_np_err = np.seterr(all='raise')
		try:
			result = np.sqrt(im1Norm + im2Norm - 2*total)
		except FloatingPointError as fpe:
			print("Error: %s" % str(fpe))
			print("im1Norm: %s, im2Norm: %s, total: %s" % (str(im1Norm),
				str(im2Norm),
				str(total)))
			raise fpe
		np.seterr(**existing_np_err)
		return result
	elif (len(i1_s) == 3):
		distance = 0
		for x in range(i1_s[0]):
			for y in range(i1_s[1]):
				for z in range(i1_s[2]):
					if im1[x][y][z] == im2[x][y][z]:
						continue
					distance += abs(im1[x][y][z] - im1[x][y][z])**2
		return (distance / (i1_s[0] * i1_s[1] * i1_s[2]))**(1/2)

def norm(img):
	y,x = img.shape
	total = 0
	for a in range(y):
		for b in range(x):
			total += img[a][b]**2
	return total

def TestD():
	i1 = np.array(Image.open("test_inputs/checker.jpg").convert('L'),dtype="float")
	i2 = np.array(Image.open("test_inputs/checker_grad.jpg").convert('L'),dtype="float")
	i3 = np.array(Image.open("test_inputs/checker_blur.jpg").convert('L'),dtype="float")
	
	i1Norm = norm(i1)
	i2Norm = norm(i2)
	i3Norm = norm(i3)
	
	d11 = d(i1,i1,i1Norm,i1Norm)
	d22 = d(i2,i2,i2Norm,i2Norm)
	print "\nd(i1,i1) =", d11
	print "d(i2,i2) =", d22

	# test2: symmetry
	d12 = d(i1,i2,i1Norm,i2Norm)
	d21 = d(i2,i1,i2Norm,i1Norm)
	print "\nd(i1,i2) =", d12
	print "d(i2,i1) =", d21

	# test3: triangle inequality
	d23 = d(i2,i3,i2Norm,i3Norm)
	d13 = d(i1,i3,i1Norm,i3Norm)
	print "\nd(i1,i2) =", d12
	print "d(i2,i3) =", d23
	print "d(i1,i3) =", d13
	print "d(i1,i3) =< d(i1,i2) + d(i2,i3)"
	print "d(i1,i3) >= abs(d(i1,i2) - d(i2,i3))"
	print abs(d12 - d23), "<=", d13, "<=", d12 + d23, "\n"

if __name__ == "__main__":
	TestD()
