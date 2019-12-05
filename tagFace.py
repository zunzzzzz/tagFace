"""
Title: tagFace.py
Author: Hsin-Yu Chien
Description: The program can search pictures and let users tag the faces in the picture manually 
User guide:
	=================
	How to use
	=================
	1. Put the tagFace.py under the folder where you want to search pictures recursively
	2. Open the terminal and execute the command "python tagFace.py" to start the program
	3. The program will search pictures and show in a window
	4. Click left key of mouse to start draw a rectangle, hold the left key and move mouse to exapnd the rectangle, release the left key to fix the size of the rectangle
	5. There are three buttons on the canvas:
	
		"Undo": Undo the last rectangle
		"Clear": Clear all the rectangles
		"Ouput Coordinate": Ouput coordinate of all rectangles and switch to the next pictures 

	6. Directly click the "Ouput Coordinate" button for pictures with no faces, it will output a file and denote there's no faces by the filename
	7. Searched pictures path and face number will be shown on the consle while outputing files, so that you can check if the number is right immediately

	=================
	Output file path
	=================

	Output file will be under the same folder as the picture.
	If there's no face in the picture, file name will end as "_face0.txt", otherwise as "_face.txt"

	=================
	Output file content
	=================

	Output file contains several lines of coordinate of faces.
	The coordinate consists of four numbers: x0, y0, x1, y1, which denotes a point and its diagonal point of the rectangle.

	=================
	Supplement
	=================

	If seeing error-log 'Recursion error: maximum recursion depth exceeded in comparison' during execution, means there're too many pictures in the stack. Just reopen the tool and everything will work fine!
"""

import os
import sys
# Library for canvas window
from tkinter import *
# Library for image processing
from PIL import Image, ImageTk

tk = None
canvas = None
picture = None

# Current rectangle id & rectangle coordinates
rectid = None
rectx0 = 0
recty0 = 0
rectx1 = 0
recty1 = 0
# All rectangles' id
allFaceRect = []

allImagePath = []
allOutputPath = []
image_width = 0
image_height = 0
resize_ratio = 0
maxCoordinateX = 0
maxCoordinateY = 0

def startRect(event):
	global canvas, rectid, rectx0, recty0, rectx1, recty1
	# Translate mouse screen coordinates to canvas coordinates
	rectx0 = canvas.canvasx(event.x)
	recty0 = canvas.canvasy(event.y)
	# Create a rectangle object on the canvas
	rectid = canvas.create_rectangle(rectx0, recty0, rectx0, recty0, fill="", outline="#39FF14", width=3)

def movingRect(event):
	global canvas, rectid, rectx0, recty0, rectx1, recty1, maxCoordinateX, maxCoordinateY
	# Translate mouse screen coordinates to canvas coordinates
	rectx1 = canvas.canvasx(event.x)
	recty1 = canvas.canvasy(event.y)
	# Force the coordinate to be in the range of canvas's size
	if(rectx1 > maxCoordinateX):
		rectx1 = maxCoordinateX
	elif(rectx1 < 1):
		rectx1 = 1
	if(recty1 > maxCoordinateY):
		recty1 = maxCoordinateX
	elif(recty1 < 1):
		recty1 = 1
	# Update coordinates when moving the cursor
	canvas.coords(rectid, rectx0, recty0, rectx1, recty1)

def stopRect(event):
	global canvas, rectid, rectx0, recty0, rectx1, recty1, allFaceRect, maxCoordinateX, maxCoordinateY
	# Translate mouse screen x1,y1 coordinates to canvas coordinates
	rectx1 = canvas.canvasx(event.x)
	recty1 = canvas.canvasy(event.y)
	# Force the coordinate to be in the range of canvas's size
	if(rectx1 > maxCoordinateX):
		rectx1 = maxCoordinateX
	elif(rectx1 < 1):
		rectx1 = 1
	if(recty1 > maxCoordinateY):
		recty1 = maxCoordinateY
	elif(recty1 < 1):
		recty1 = 1
	# Update coordinates
	canvas.coords(rectid, rectx0, recty0, rectx1, recty1)
	# Store the rectangle id to the array
	allFaceRect.append(rectid)

def clickUndo():
	# Delete the latest rectangle
	global canvas, allFaceRect
	if(len(allFaceRect)>0):
		canvas.delete(allFaceRect[-1])
		del(allFaceRect[-1])

def clickClear():
	# Clear all rectangles' id
	global canvas, allFaceRect
	for rectid in allFaceRect:
		canvas.delete(rectid)
	allFaceRect = []

def clickOutput():
	global canvas, allFaceRect, allOutputPath, allImagePath, image_width, image_height, resize_ratio
	outputPath = allOutputPath.pop(0)
	# If there's no face in the picture, file name will end as "_face0.txt"
	if(len(allFaceRect) == 0):
		outputFile = open(outputPath+"0.txt", "w")
	else:
		outputFile = open(outputPath+".txt", "w")
	print("======================================")
	print("Face Number = "+str(len(allFaceRect)))

	# Write coordinates to the output file
	for rect in allFaceRect:
		x0 = int(canvas.coords(rect)[0]/resize_ratio)
		y0 = int(canvas.coords(rect)[1]/resize_ratio)
		x1 = int(canvas.coords(rect)[2]/resize_ratio)
		y1 = int(canvas.coords(rect)[3]/resize_ratio)
		if(x1 >= image_width):
			x1 = image_width-1
		if(y1 >= image_height):
			y1 = image_height-1
		outputFile.write(str(x0)+", ")
		outputFile.write(str(y0)+", ")
		outputFile.write(str(x1)+", ")
		outputFile.write(str(x1)+"\n")
	outputFile.close()

	# Clear all rectangle
	clickClear()
	# See if need to tag another picture
	if(len(allImagePath)):
		# Initial the canvas
		canvas.delete("all")
		initialCanvas(allImagePath.pop(0))
	else:
		print("======================================")
		print("All pictures are done!")
		sys.exit(0)

def initialCanvas(imagePath):
	print("======================================")
	print(imagePath)

	global tk, canvas, picture, maxCoordinateX, maxCoordinateY, image_width, image_height, resize_ratio
	# Get size of img
	image = Image.open(imagePath)
	image_width, image_height = image.size
	# Get size of screen
	screen_width = tk.winfo_screenwidth()
	screen_height = tk.winfo_screenheight()

	# Resize image to match the screen size
	resize_ratio = 1
	while(image_width*resize_ratio>screen_width or image_height*resize_ratio>screen_height):
		resize_ratio -= 0.1
		# resize_ration can't be zero
		if(resize_ratio == 0.1):
			break
	resize_image_width = int(image_width * resize_ratio)
	resize_image_height = int(image_width * resize_ratio)
	resize_image = image.resize((resize_image_width, resize_image_height))
	# Create picture object
	picture = ImageTk.PhotoImage(resize_image)
	# Set max coordinate as picture's width and height
	maxCoordinateX = resize_image_width
	maxCoordinateY = resize_image_height
	
	# Only create canvas window for the first image
	if(canvas == None):
		canvas = Canvas(width=resize_image_width, height=resize_image_height, bg='white')
		canvas.pack(expand=True)
	else:
		canvas.config(width=resize_image_width, height=resize_image_height)
	
	# Set img as background of the canvas
	canvas.create_image(int(resize_image_width/2), int(resize_image_height/2), image=picture)

	# Create "Undo" button
	button0 = Button(text = "Undo", anchor=CENTER, bd=2, command=clickUndo)
	button0.configure(activebackground="#33B5E5", relief=SUNKEN)
	canvas.create_window(10, 10, anchor=NW, window=button0)
	# Create "Clear" button
	button1 = Button(text = "Clear", anchor=CENTER, bd=2, command=clickClear)
	button1.configure(activebackground="#33B5E5", relief=SUNKEN)
	canvas.create_window(65, 10, anchor=NW, window=button1)
	# Create "Ouput Coordinate" button
	button2 = Button(text = "Ouput Coordinate", anchor=CENTER, bd=2, command=clickOutput)
	button2.configure(activebackground="#33B5E5", relief=SUNKEN)
	canvas.create_window(125, 10, anchor=NW, window=button2)
	
	# Bind button events
	canvas.bind( "<Button-1>", startRect)
	canvas.bind( "<B1-Motion>", movingRect)
	canvas.bind( "<ButtonRelease-1>", stopRect)
	# Update the canvas after create above objects
	tk.mainloop()

# Get current path
rootPath = os.getcwd()

# Recursively search files from the current path
for root, dirs, files in os.walk(rootPath):
	# Find jpg or png pictures
	for file in files:
		filePath = os.path.join(root, file)
		if (filePath[-3:] == "jpg" or filePath[-3:] == "png"):
			# Push the image in to the array and wait for tag faces
			allImagePath.append(filePath)
			# Push the output file path to the array and wait for output
			allOutputPath.append(filePath[0:-4]+'_face')
		# If there're 10 images in the array, break 
		if (len(allImagePath) >= 10):
			break
	if (len(allImagePath) >= 10):
		break

if (len(allImagePath)):
	tk = Tk()
	# Disable window-resizing
	tk.resizable(0, 0)
	initialCanvas(allImagePath.pop(0))
else:
    print("Image not found!")
