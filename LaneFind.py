from PIL import ImageGrab,Image
import cv2
import numpy as np
import time
import math
import statistics as st


#Get each frame from the gta region


#With drawing the lanes, I am going to average out each poition of the hough to draw overall lanes
#Then I can seperate the lines


#Now send in the different end points of the line

		

#192 490
#348 378
#I am going to max out the averages,then average the max values then the current calc averages
#Find max and mins of the values
max_x_average_before_right = 0
max_y_average_before_right = 0
nc_right = 0
def max_average_right(xAVG,yAVG):
	global nc_right
	global max_x_average_before_right
	global max_y_average_before_right
	nc_right += 1
	if nc_right % 25 == 0:
		max_x_average_before_right = 0
		max_y_average_before_right = 0
		print 'here'
		if nc_right == 500:
			nc_right = 0

	if max_x_average_before_right <= xAVG:
		max_x_average_before_right = xAVG
	if max_y_average_before_right <= yAVG:
		max_y_average_before_right = yAVG
	return max_x_average_before_right,max_y_average_before_right

max_x_average_before_left = 0
max_y_average_before_left = 0
nc_left = 0
def max_average_left(xAVG,yAVG):
	global max_x_average_before_left
	global max_y_average_before_left
	global nc_left
	nc_left += 1
	if nc_left % 25 == 0:
		max_x_average_before_left = 0
		max_y_average_before_left = 0
	if nc_left == 500:
		nc_left = 0
	if max_x_average_before_left <= xAVG:
		max_x_average_before_left = xAVG
	if max_y_average_before_left <= yAVG:
		max_y_average_before_left = yAVG
	return max_x_average_before_left,max_y_average_before_left

def average_lines(xPointBefore,yPointBefore,xPointAfter,yPointAfter):
	xAVG = (np.array(xPointBefore) + np.array(xPointAfter)) / 2
	yAVG = (np.array(yPointBefore) + np.array(yPointAfter)) / 2
	#We are going to want to return the highest average
	return xAVG,yAVG

#A single indexed array that contains the end points of the line
line_before_right = [0,0]
line_before_left = [0,0]

def manage_lines(screen,lines):
	global line_before_right
	global line_before_left
	for line in lines:
		for x1,y1,x2,y2 in line:
			slope = (y2 - y1)/(x2 - x1)
			if slope == -1:
				print line_before_left
				xPointBefore = line_before_left[0]
				yPointBefore = line_before_left[1]
				line_before_left = [] #Init new array
				#Send to function
				
				left_end_pointsX,left_end_pointsY = average_lines(xPointBefore,yPointBefore,x1,y1)
				left_end_pointsX,left_end_pointsY = max_average_left(left_end_pointsX,left_end_pointsY)
				line_before_left.append(left_end_pointsX)
				line_before_left.append(left_end_pointsY)
				cv2.line(screen,(int(196),int(486)),(x2,y2),[255,255,255],2)
				#print left_end_pointsX,left_end_pointsY, 'THIS IS LEFT'
			elif slope == 0:
				xPointBefore = line_before_right[0]
				yPointBefore = line_before_right[1]
				line_before_right = [] #Init new array
				#Send to function
				right_end_pointsX,right_end_pointsY = average_lines(xPointBefore,yPointBefore,x1,y1)
				right_end_pointsX,right_end_pointsY = max_average_right(right_end_pointsX,right_end_pointsY)
				line_before_right.append(right_end_pointsX)
				line_before_right.append(right_end_pointsY)
				cv2.line(screen,(int(right_end_pointsX),int(right_end_pointsY)),(x2,y2),[255,255,255],2)
				#print right_end_pointsX,right_end_pointsY, 'THIS IS RIGHT'

def roi(screen, vertices):
	mask = np.zeros_like(screen,dtype=np.uint8)
	cv2.fillPoly(mask,np.int32([vertices]),255)
	masked_image = cv2.bitwise_and(screen, mask)
	return masked_image
	
	
	
def color_selection(screen):
	hls = cv2.cvtColor(screen,cv2.COLOR_RGB2HLS)
	lower_white = np.uint8([20,200,0])
	upper_white = np.uint8([255,255,255])
	#Now make a range for the white color
	white_color = cv2.inRange(hls,lower_white,upper_white)
	
	lower_yellow = np.uint8([10,50,100])
	upper_yellow = np.uint8([100,255,255])
	
	#Make the range for the yellow color
	yellow_color = cv2.inRange(hls,lower_yellow,upper_yellow)
	
	comb = cv2.bitwise_or(white_color,yellow_color)
	return cv2.bitwise_and(screen, screen, mask = comb)

def draw_circle(event,x,y,flags,param):
	if event == cv2.EVENT_LBUTTONDBLCLK:
		print x,y

def processImage(org_screen):
	org_screen = color_selection(org_screen)
	org_screen = cv2.cvtColor(org_screen,cv2.COLOR_BGR2GRAY)
	org_screen = cv2.GaussianBlur(org_screen, (5,5), 0)
	org_screen = cv2.Canny(org_screen,50,160)
	vertices = np.array([[107,492],[382,343],[458,352],[720,491]])
	org_screen = roi(org_screen,vertices)
	lines = cv2.HoughLinesP(org_screen,2,np.pi/180,2,20,5)
	array = manage_lines(org_screen,lines)
	

	return org_screen
	
def timer(cont):
	for i in range(cont):
		cont = cont - 1
		time.sleep(1)
		print cont

def main():
	timer(20)
	while 1:
		screen = np.array(ImageGrab.grab(bbox=(0,40,800,600)))
		screen = processImage(screen)
		cv2.imshow('window',screen)
		cv2.setMouseCallback('window',draw_circle)
		if cv2.waitKey(25) & 0xFF == ord('q'):
			cv2.destroyAllWindows()
			break
			

	
main()