'''
*****************************************************************************************
*
*        =================================================
*             Pharma Bot Theme (eYRC 2022-23)
*        =================================================
*                                                         
*  This script is intended for implementation of Task 2B   
*  of Pharma Bot (PB) Theme (eYRC 2022-23).
*
*  Filename:			task_2b.py
*  Created:				
*  Last Modified:		8/10/2022
*  Author:				e-Yantra Team
*  
*  This software is made available on an "AS IS WHERE IS BASIS".
*  Licensee/end user indemnifies and will keep e-Yantra indemnified from
*  any and all claim(s) that emanate from the use of the Software or 
*  breach of the terms of this agreement.
*
*****************************************************************************************
'''

# Team ID:			[ Team-ID ]
# Author List:		[ Names of team members worked on this file separated by Comma: Name1, Name2, ... ]
# Filename:			task_2b.py
# Functions:		control_logic, read_qr_code
# 					[ Comma separated list of functions in this file ]
# Global variables:	
# 					[ List of global variables defined in this file ]

####################### IMPORT MODULES #######################
## You are not allowed to make any changes in this section. ##
##############################################################
import  sys
import traceback
import time
import os
import math
from zmqRemoteApi import RemoteAPIClient
import zmq
import numpy as np
import cv2
import random
from pyzbar.pyzbar import decode
##############################################################
graph={'A1': {'B1': 1, 'A2': 1}, 'B1': {'C1': 1, 'A1': 1, 'B2': 1}, 'C1': {'D1': 1, 'B1': 1, 'C2': 1}, 'D1': {'E1': 1, 'C1': 1, 'D2': 1}, 'E1': {'F1': 1, 'D1': 1, 'E2': 1}, 'F1': {'E1': 1, 'F2': 1}, 'A2': {'B2': 1, 'A3': 1, 'A1': 1}, 'B2': {'C2': 1, 'A2': 1, 'B3': 1, 'B1': 1}, 'C2': {'D2': 1, 'B2': 1, 'C3': 1, 
'C1': 1}, 'D2': {'E2': 1, 'C2': 1, 'D1': 1}, 'E2': 
{'F2': 1, 'D2': 1, 'E3': 1, 'E1': 1}, 'F2': {'E2': 
1, 'F3': 1, 'F1': 1}, 'A3': {'B3': 1, 'A4': 1, 'A2': 1}, 'B3': {'A3': 1, 'B2': 1}, 'C3': {'D3': 1, 'C2': 1}, 'D3': {'E3': 1, 'C3': 1}, 'E3': {'F3': 1, 'D3': 1, 'E4': 1, 'E2': 1}, 'F3': {'E3': 1, 'F2': 1}, 'A4': {'B4': 1, 'A5': 1, 'A3': 1}, 'B4': {'C4': 1, 'A4': 1, 'B5': 1}, 'C4': {'D4': 1, 'B4': 1, 'C5': 
1}, 'D4': {'E4': 1, 'C4': 1, 'D5': 1}, 'E4': {'D4': 1, 'E3': 1}, 'F4': {'F5': 1}, 'A5': {'B5': 1, 'A6': 1, 'A4': 1}, 'B5': {'C5': 1, 'A5': 1, 'B4': 1}, 'C5': {'D5': 1, 'B5': 1, 'C6': 1, 'C4': 1}, 'D5': {'E5': 1, 'C5': 1, 'D4': 1}, 'E5': {'F5': 1, 'D5': 1, 'E6': 1}, 'F5': {'E5': 1, 'F4': 1}, 'A6': {'B6': 1, 'A5': 1}, 'B6': {'A6': 1}, 'C6': {'D6': 1, 'C5': 
1}, 'D6': {'E6': 1, 'C6': 1}, 'E6': {'F6': 1, 'D6': 1, 'E5': 1}, 'F6': {'E6': 1}}

################# ADD UTILITY FUNCTIONS HERE #################
def path_planning(graph, start, end):
	backtrace_path = []
	visited = []
	queue = []
	parent = {}
	queue.append(start)
	visited.append(start)
	parent[start] = -1
	while (len(queue) > 0):
		front = queue[0]
		queue.pop(0)
		for key in graph[front]:
			if (visited.count(key) == 0):
				queue.append(key)
				parent[key] = front
				visited.append(key)
				if (key == end):
					queue.clear()
					break

	while (end != -1):
		backtrace_path.insert(0, end)
		end = parent[end]
	return backtrace_path


def paths_to_moves(paths,curdirection):
	list_moves = []
	curnode = paths[0]
	temp = len(paths)
	print("printing_path")
	print(paths)
	for i in range(1, temp):
		newnode = paths[i]
		if (ord(newnode[0])-ord(curnode[0]) != 0):
			if (ord(newnode[0])-ord(curnode[0]) == 1):
				tomove = 'right'
			else:
				tomove = 'left'
		else:
			if (ord(newnode[1])-ord(curnode[1]) != 0):
				if (ord(newnode[1])-ord(curnode[1]) == 1):
					tomove = 'down'
				else:
					tomove = 'straight'
		# if (traffic_signal.count(curnode) > 0):
		# 	list_moves.append("W")
		curnode = newnode
		if (tomove == 'left'):
			if (curdirection == 'N'):
				list_moves.append('L')
			elif (curdirection == 'S'):
				list_moves.append('R')
			elif (curdirection == 'W'):
				list_moves.append('S')
			elif (curdirection == 'E'):
				list_moves.append('v')
				list_moves.append('S')
			curdirection = 'W'
		elif (tomove == 'right'):
			if (curdirection == 'N'):
				list_moves.append('R')
			elif (curdirection == 'S'):
				list_moves.append('L')
			elif (curdirection == 'W'):
				list_moves.append('v')
				list_moves.append('S')
			elif (curdirection == 'E'):
				list_moves.append('S')
			curdirection = 'E'
		elif (tomove == 'straight'):
			if (curdirection == 'N'):
				list_moves.append('S')
			elif (curdirection == 'S'):
				list_moves.append('v')
				list_moves.append('S')
			elif (curdirection == 'W'):
				list_moves.append('R')
			elif (curdirection == 'E'):
				list_moves.append('L')
			curdirection = 'N'
		elif (tomove == 'down'):
			if (curdirection == 'N'):
				list_moves.append('v')
				list_moves.append('S')
			elif (curdirection == 'S'):
				list_moves.append('S')
			elif (curdirection == 'W'):
				list_moves.append('L')
			elif (curdirection == 'E'):
				list_moves.append('R')
			curdirection = 'S'
	listmoves1=''
	for i in list_moves:
		listmoves1+=i
	return (listmoves1,curdirection)

def turn_left(sim):
	rightjoint = sim.getObjectHandle('/Diff_Drive_Bot/right_joint')
	leftjoint = sim.getObjectHandle('/Diff_Drive_Bot/left_joint')
	camera=sim.getObjectHandle('/Diff_Drive_Bot/vision_sensor')
	img,resolution=sim.getVisionSensorImg(camera,1,0.0,[0,0],[0,0])
	sim.setJointTargetVelocity(rightjoint,3.3)
	sim.setJointTargetVelocity(leftjoint, -3.3)
	time.sleep(0.15)
	# print('hi')
	while(img[261175]>200):
		# print(img[261175])
		img,resolution=sim.getVisionSensorImg(camera,1,0.0,[0,0],[0,0])
	# print('alright...')
	img,resolution=sim.getVisionSensorImg(camera,1,0.0,[0,0],[0,0])
	
	while(img[261350]>200):
		# print(img[261480])
		img,resolution=sim.getVisionSensorImg(camera,1,0.0,[0,0],[0,0])

	all_stop(sim)
	all_run(sim)
		
def turn_right(sim,turns):
	rightjoint = sim.getObjectHandle('/Diff_Drive_Bot/right_joint')
	leftjoint = sim.getObjectHandle('/Diff_Drive_Bot/left_joint')
	camera=sim.getObjectHandle('/Diff_Drive_Bot/vision_sensor')
	sim.setJointTargetVelocity(rightjoint,-3.3)
	sim.setJointTargetVelocity(leftjoint,3.3)
	if(turns==12):
		time.sleep(0.050)
		tt=261350
		pass
	else:
		tt=261360
		time.sleep(0.15)
	img,resolution=sim.getVisionSensorImg(camera,1,0.0,[0,0],[0,0])
	while(img[261610]>200):
		img,resolution=sim.getVisionSensorImg(camera,1,0.0,[0,0],[0,0])
	img,resolution=sim.getVisionSensorImg(camera,1,0.0,[0,0],[0,0])
	
	while(img[tt]>200):
		img,resolution=sim.getVisionSensorImg(camera,1,0.0,[0,0],[0,0])
	all_stop(sim)
def go_back(sim):
		rightjoint = sim.getObjectHandle('/Diff_Drive_Bot/right_joint')
		sim.setJointTargetVelocity(rightjoint, -1)
		leftjoint = sim.getObjectHandle('/Diff_Drive_Bot/left_joint')
		sim.setJointTargetVelocity(leftjoint, -1)
		time.sleep(0.5)		

def turn_rev(sim):
	turn_right(sim,12)
	turn_right(sim,12)




def all_stop(sim):

		rightjoint = sim.getObjectHandle('/Diff_Drive_Bot/right_joint')
		sim.setJointTargetVelocity(rightjoint, 0)
		leftjoint = sim.getObjectHandle('/Diff_Drive_Bot/left_joint')
		sim.setJointTargetVelocity(leftjoint, 0)

def all_run(sim):

		rightjoint = sim.getObjectHandle('/Diff_Drive_Bot/right_joint')
		sim.setJointTargetVelocity(rightjoint, speed)
		leftjoint = sim.getObjectHandle('/Diff_Drive_Bot/left_joint')
		sim.setJointTargetVelocity(leftjoint, speed)
		time.sleep(0.025)

# def activate_qr(sim,cnt):
# 	if(cnt==1):
# 		arena_dummy_handle = sim.getObject("/Arena_dummy") 
# 		childscript_handle = sim.getScript(sim.scripttype_childscript, arena_dummy_handle, "")
# 		sim.callScriptFunction("activate_qr_code", childscript_handle, "checkpoint E")

# 	if(cnt==2):
# 		# print('activating 2')
# 		arena_dummy_handle = sim.getObject("/Arena_dummy") 
# 		childscript_handle = sim.getScript(sim.scripttype_childscript, arena_dummy_handle, "")
# 		sim.callScriptFunction("activate_qr_code", childscript_handle, "checkpoint I")

# 	if(cnt==3):
# 		# print('activating 3')
# 		arena_dummy_handle = sim.getObject("/Arena_dummy") 
# 		childscript_handle = sim.getScript(sim.scripttype_childscript, arena_dummy_handle, "")
# 		sim.callScriptFunction("activate_qr_code", childscript_handle, "checkpoint M")


# def deactivate_qr(sim,cnt):
# 	if(cnt==1):
# 		arena_dummy_handle = sim.getObject("/Arena_dummy") 
# 		childscript_handle = sim.getScript(sim.scripttype_childscript, arena_dummy_handle, "")
# 		sim.callScriptFunction("deactivate_qr_code", childscript_handle, "checkpoint E")
		

# 	if(cnt==2):
# 			# print('activating 2')

# 			arena_dummy_handle = sim.getObject("/Arena_dummy") 
# 			childscript_handle = sim.getScript(sim.scripttype_childscript, arena_dummy_handle, "")
# 			sim.callScriptFunction("deactivate_qr_code", childscript_handle, "checkpoint I")
			

# 	if(cnt==3):
# 		# print('activating 3')

# 		arena_dummy_handle = sim.getObject("/Arena_dummy") 
# 		childscript_handle = sim.getScript(sim.scripttype_childscript, arena_dummy_handle, "")
# 		sim.callScriptFunction("deactivate_qr_code", childscript_handle, "checkpoint M")
		
	
speed=1.15
tspeed=1.25
##############################################################

def control_logic(sim):
	
	all_stop(sim)
	##############  ADD YOUR CODE HERE  ##############
	what_to_deliver = 1
	turns=1
	flag=0
	spflag=0
	corr=0.01
	tcorr=0.65
	# m={1:1,2:2,3:1,4:2,5:0,6:2,7:1,8:2,9:0,10:2,11:1,12:2,13:0,14:2,15:1,16:2,17:3}
	# qr={1:0,2:0,3:0,4:0,5:1,6:0,7:0,8:0,9:1,10:0,11:0,12:0,13:1,14:0,15:0,16:0,17:0}
	location={ 'A1':[-0.6150,-0.4750,0.0710],'B1':[-0.3900,0.4750,0.0710],'C1':[-0.1400,0.4750,0.0710],'D1':[0.0850,0.4750,0.0710],'E1':[0.3350,0.4750,0.0710],'F1':[0.5600,0.4750,0.0710],
			 		   'A2':[-0.6150,0.2250,0.0710], 'B2':[-0.3900,0.2250,0.0710],'C2':[-0.1400,0.2250,0.0710],'D2':[0.0850,0.2250,0.0710],'E2':[0.3350,0.2250,0.0710],'F2':[0.5600,0.2250,0.0710],
					   'A3':[-0.6150,0.000026,0.0710],'B3':[-0.3900,0.000026,0.0710],'C3':[-0.1400,0.000026,0.0710],'D3':[0.0850,0.000026,0.0710],'E3':[0.3350,0.000026,0.0710],'F3':[0.5600,0.000026,0.0710],
					   'A4':[-0.6150,-0.2500,0.0710], 'B4':[-0.3900,-0.2500,0.0710],'C4':[-0.1400,-0.2500,0.0710],'D4':[0.0850,-0.2500,0.0710],'E4':[0.3350,-0.2500,0.0710],'F4':[0.5600,-0.2500,0.0710],
					   'A5':[-0.6150,-0.4750,0.0710], 'B5':[-0.3900,-0.4750,0.0710],'C5':[-0.1400,-0.4750,0.0710],'D5':[0.0850,-0.4750,0.0710],'E5':[0.3350,-0.4750,0.0710],'F5':[0.5600,-0.4750,0.0710],
					   'A6':[-0.6150,-0.7000,0.0710], 'B6':[-0.3900,-0.7000,0.0710],'C6':[-0.1400,-0.7000,0.0710],'D6':[0.0850,-0.7000,0.0710],'E6':[0.3350,-0.7000,0.0710],'F6':[0.5600,-0.7000,0.074750]}
	
	cnt=1
	slowed=0
	strptr=0
	cd='N'
	nodes=[]
	n=int(input("enter the number of nodes"))
	for i1 in range(0,n):
		temp=input("enter node")
		nodes.append(temp)
	st=nodes[0]
	print(nodes)
	i1=1


	while(i1<n):
		print("current value of i is ",i1)
	
		all_stop(sim)
		en=nodes[i1]
		i1+=1

		if(st=="-1" or en=="-1"):
			break
		seq=path_planning(graph,st,en)
		mov1,cd=paths_to_moves(seq,cd)
		print(mov1)
		mov=mov1+"T"
		st = en
	
		rightjoint = sim.getObjectHandle('/Diff_Drive_Bot/right_joint')
		sim.setJointTargetVelocity(rightjoint, speed)
		leftjoint = sim.getObjectHandle('/Diff_Drive_Bot/left_joint')
		sim.setJointTargetVelocity(leftjoint, speed)
		camera=sim.getObjectHandle('/Diff_Drive_Bot/vision_sensor')

		while(True):
			img,resolution=sim.getVisionSensorImg(camera,1,0.0,[0,0],[0,0])
			# print(img[1791])
			leftcorr=img[261175]
			# print(leftcorr)
			rightcorr=img[261610]	
			if( not spflag):
				ct=0
				for i in range(76880,77240):
					if(img[i]>180):
						ct+=1

				if(ct>200):
					spflag=1
			

			if(not spflag):
				slowed=0
				if(leftcorr<240 and rightcorr>240):
					sim.setJointTargetVelocity(leftjoint, tspeed-tcorr)
					sim.setJointTargetVelocity(rightjoint, tspeed+tcorr)
					# print('   left')
				elif(leftcorr>240 and rightcorr<240):
					sim.setJointTargetVelocity(leftjoint, tspeed+tcorr)
					sim.setJointTargetVelocity(rightjoint, tspeed-tcorr)
					# print(   'right')
				else:
					sim.setJointTargetVelocity(leftjoint, tspeed)
					sim.setJointTargetVelocity(rightjoint, tspeed)
					# print('   straight')
			elif(spflag and (not slowed)):
				slowed=1
				# if(qr[turns] ):
				# 	time.sleep(0.0008)
				# 	# print('qr.....')
				# 	# read_qr_code(sim,cnt)
				# 	cnt+=1
				# 	time.sleep(0.001)
				# else:
				time.sleep(1)
				# print("time")
				if(leftcorr<240 and rightcorr>240):	
					sim.setJointTargetVelocity(leftjoint, speed-corr)
					sim.setJointTargetVelocity(rightjoint, speed+corr)
					# print('   left')
				elif(leftcorr>240 and rightcorr<240):
					sim.setJointTargetVelocity(leftjoint, speed+corr)
					sim.setJointTargetVelocity(rightjoint, speed-corr)
					# print(   'right')
				else:
					sim.setJointTargetVelocity(leftjoint, speed)
					sim.setJointTargetVelocity(rightjoint, speed)

		#######################################################################
			# print(img[255] )
			if(img[255]==85 or img[1791]==85 or img[3327]==85  ):#    or img[4863]<130
					read_qr_code(sim,0,what_to_deliver,-2,location,en)

					
					

					time.sleep(0.3)
					
					if(mov[strptr]=='L'):
						all_stop(sim)
						turn_left(sim)
						print("left")
						
					elif(mov[strptr]=='S'):
						# print('hi................')
						time.sleep(0.01)
						spflag=0
						pass
					elif(mov[strptr]=='R'):
						# time.sleep(0.05)
						all_stop(sim)
						turn_right(sim,turns)
						print("right")
					elif(mov[strptr]=='v'):
						strptr+=1
						all_stop(sim)
						turn_rev(sim)
						all_run(sim)
						print("180 turning")

					elif(mov[strptr]=='T'):
						read_qr_code(sim,0,what_to_deliver,-1,location,en)
						what_to_deliver+=1
						all_stop(sim)
						go_back(sim)
						all_stop(sim)
						strptr = 0
						print("value of i is ",i1)
						break
					flag=0
					spflag=0
					turns+=1					
					time.sleep(0.0080)
					strptr+=1 
#########################################################################		


cntx=1
def read_qr_code(sim,cntx,what_to_deliver,k,location,en):
	if k == -2:
		return
	
	# qr_message = None
	# ##############  ADD YOUR CODE HERE  ##############
	# all_stop(sim)
	# activate_qr(sim,cntx)
	# camera=sim.getObjectHandle('/Diff_Drive_Bot/vision_sensor')
	# img,resolution=sim.getVisionSensorImg(camera,0,0.0,[0,0],[0,0])
	# ls=[]
	# for i in range(0,786432):
	# 	ls.insert(i,img[i])

	# arr=np.array(ls,dtype=np.uint8)
	# arr.resize([512,512,3])
	# arr = cv2.cvtColor(arr, cv2.COLOR_RGB2BGR)
	
	# for qrcode in decode(arr):
	# 	qrcode=qrcode.data.decode('utf-8')
	# 	# print(qrcode)
	# deactivate_qr(sim,cntx)
	# pack={'Orange Cone':'package_1','Blue Cylinder':'package_2','Pink Cuboid': 'package_3'}

	# if(cntx==1):
	# 	arena_dummy_handle = sim.getObject("/Arena_dummy") 
	# 	childscript_handle = sim.getScript(sim.scripttype_childscript, arena_dummy_handle, "")
	# 	sim.callScriptFunction("deliver_package", childscript_handle, pack[qrcode], "checkpoint E")

	# if(cntx==2):
	if(what_to_deliver==1):
		arena_dummy_handle = sim.getObjectHandle("/Diff_Drive_Bot/tray_joint/package_1") 
		sim.setObjectPosition(arena_dummy_handle, -1, location[en])
		arena = sim.getObjectHandle('/Arena')
		sim.setObjectParent(arena_dummy_handle, arena, 0) 
	if(what_to_deliver==2):
		arena_dummy_handle = sim.getObjectHandle("/Diff_Drive_Bot/tray_joint/package_2") 
		sim.setObjectPosition(arena_dummy_handle, -1,location[en] )
		arena = sim.getObjectHandle('/Arena')
		sim.setObjectParent(arena_dummy_handle, arena, 0) 
	if(what_to_deliver==3):
		arena_dummy_handle = sim.getObjectHandle("/Diff_Drive_Bot/tray_joint/package_3") 
		sim.setObjectPosition(arena_dummy_handle, -1,location[en] )
		arena = sim.getObjectHandle('/Arena')
		sim.setObjectParent(arena_dummy_handle, arena, 0) 
	# childscript_handle = sim.getScript(sim.scripttype_childscript, arena_dummy_handle, "")
	# sim.callScriptFunction("deliver_package", childscript_handle,'package_1', "checkpoint I")

	# if(cntx==3):
		# arena_dummy_handle = sim.getObject("/Arena_dummy") 
		# childscript_handle = sim.getScript(sim.scripttype_childscript, arena_dummy_handle, "")
		# sim.callScriptFunction("deliver_package", childscript_handle, pack[qrcode], "checkpoint M")

	all_run(sim)
	##################################################
	# return qr_message


######### YOU ARE NOT ALLOWED TO MAKE CHANGES TO THE MAIN CODE BELOW #########

if __name__ == "__main__":
	client = RemoteAPIClient()
	sim = client.getObject('sim')	

	try:

		## Start the simulation using ZeroMQ RemoteAPI
		try:
			return_code = sim.startSimulation()
			if sim.getSimulationState() != sim.simulation_stopped:
				print('\nSimulation started correctly in CoppeliaSim.')
			else:
				print('\nSimulation could not be started correctly in CoppeliaSim.')
				sys.exit()

		except Exception:
			# print('\n[ERROR] Simulation could not be started !!')
			traceback.print_exc(file=sys.stdout)
			sys.exit()

		## Runs the robot navigation logic written by participants
		try:
			# time.sleep(5)
			control_logic(sim)

		except Exception:
			# print('\n[ERROR] Your control_logic function throwed an Exception, kindly debug your code!')
			# print('Stop the CoppeliaSim simulation manually if required.\n')
			traceback.print_exc(file=sys.stdout)
			# print()
			sys.exit()

		
		## Stop the simulation using ZeroMQ RemoteAPI
		try:
			return_code = sim.stopSimulation()
			time.sleep(0.5)
			if sim.getSimulationState() == sim.simulation_stopped:
				print('\nSimulation stopped correctly in CoppeliaSim.')
			else:
				print('\nSimulation could not be stopped correctly in CoppeliaSim.')
				sys.exit()

		except Exception:
			print('\n[ERROR] Simulation could not be stopped !!')
			traceback.print_exc(file=sys.stdout)
			sys.exit()

	except KeyboardInterrupt:
		## Stop the simulation using ZeroMQ RemoteAPI
		return_code = sim.stopSimulation()
		time.sleep(0.5)
		if sim.getSimulationState() == sim.simulation_stopped:
			print('\nSimulation interrupted by user in CoppeliaSim.')
		else:
			print('\nSimulation could not be interrupted. Stop the simulation manually .')
			sys.exit()








			