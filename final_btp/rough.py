import sys
import traceback
import time
import os
import math
from rough import control_logic
from zmqRemoteApi import RemoteAPIClient
import zmq
import numpy as np
import cv2
from pyzbar.pyzbar import decode

graph = {
    'A1': {'B1': 1, 'A2': 1}, 'B1': {'C1': 1, 'A1': 1, 'B2': 1}, 'C1': {'D1': 1, 'B1': 1, 'C2': 1},
    'D1': {'E1': 1, 'C1': 1, 'D2': 1}, 'E1': {'F1': 1, 'D1': 1, 'E2': 1}, 'F1': {'E1': 1, 'F2': 1},
    'A2': {'B2': 1, 'A3': 1, 'A1': 1}, 'B2': {'C2': 1, 'A2': 1, 'B3': 1, 'B1': 1}, 'C2': {'D2': 1, 'B2': 1, 'C3': 1, 'C1': 1},
    'D2': {'E2': 1, 'C2': 1, 'D1': 1}, 'E2': {'F2': 1, 'D2': 1, 'E3': 1, 'E1': 1}, 'F2': {'E2': 1, 'F3': 1, 'F1': 1},
    'A3': {'B3': 1, 'A4': 1, 'A2': 1}, 'B3': {'A3': 1, 'B2': 1}, 'C3': {'D3': 1, 'C2': 1},
    'D3': {'E3': 1, 'C3': 1}, 'E3': {'F3': 1, 'D3': 1, 'E4': 1, 'E2': 1}, 'F3': {'E3': 1, 'F2': 1},
    'A4': {'B4': 1, 'A5': 1, 'A3': 1}, 'B4': {'C4': 1, 'A4': 1, 'B5': 1}, 'C4': {'D4': 1, 'B4': 1, 'C5': 1},
    'D4': {'E4': 1, 'C4': 1, 'D5': 1}, 'E4': {'D4': 1, 'E3': 1}, 'F4': {'F5': 1},
    'A5': {'B5': 1, 'A6': 1, 'A4': 1}, 'B5': {'C5': 1, 'A5': 1, 'B4': 1},
    'C5': {'D5': 1, 'B5': 1, 'C6': 1, 'C4': 1}, 'D5': {'E5': 1, 'C5': 1, 'D4': 1},
    'E5': {'F5': 1, 'D5': 1, 'E6': 1}, 'F5': {'E5': 1, 'F4': 1}, 'A6': {'B6': 1, 'A5': 1},
    'B6': {'A6': 1}, 'C6': {'D6': 1, 'C5': 1}, 'D6': {'E6': 1, 'C6': 1}, 'E6': {'F6': 1, 'D6': 1, 'E5': 1},
    'F6': {'E6': 1}
}

def path_planning(graph, start, end):
    backtrace_path = []
    visited = []
    queue = []
    parent = {}
    queue.append(start)
    visited.append(start)
    parent[start] = -1
    while len(queue) > 0:
        front = queue[0]
        queue.pop(0)
        for key in graph[front]:
            if visited.count(key) == 0:
                queue.append(key)
                parent[key] = front
                visited.append(key)
                if key == end:
                    queue.clear()
                    break

    while end != -1:
        backtrace_path.insert(0, end)
        end = parent[end]
    return backtrace_path

def paths_to_moves(paths, curdirection):
    list_moves = []
    curnode = paths[0]
    temp = len(paths)
    print("printing_path")
    print(paths)
    for i in range(1, temp):
        newnode = paths[i]
        if ord(newnode[0]) - ord(curnode[0]) != 0:
            if ord(newnode[0]) - ord(curnode[0]) == 1:
                tomove = 'right'
            else:
                tomove = 'left'
        else:
            if ord(newnode[1]) - ord(curnode[1]) != 0:
                if ord(newnode[1]) - ord(curnode[1]) == 1:
                    tomove = 'down'
                else:
                    tomove = 'straight'

        curnode = newnode
        if tomove == 'left':
            if curdirection == 'N':
                list_moves.append('L')
            elif curdirection == 'S':
                list_moves.append('R')
            elif curdirection == 'W':
                list_moves.append('S')
            elif curdirection == 'E':
                list_moves.append('v')
                list_moves.append('S')
            curdirection = 'W'
        elif tomove == 'right':
            if curdirection == 'N':
                list_moves.append('R')
            elif curdirection == 'S':
                list_moves.append('L')
            elif curdirection == 'W':
                list_moves.append('v')
                list_moves.append('S')
            elif curdirection == 'E':
                list_moves.append('S')
            curdirection = 'E'
        elif tomove == 'straight':
            if curdirection == 'N':
                list_moves.append('S')
            elif curdirection == 'S':
                list_moves.append('v')
                list_moves.append('S')
            elif curdirection == 'W':
                list_moves.append('R')
            elif curdirection == 'E':
                list_moves.append('L')
            curdirection = 'N'
        elif tomove == 'down':
            if curdirection == 'N':
                list_moves.append('v')
                list_moves.append('S')
            elif curdirection == 'S':
                list_moves.append('S')
            elif curdirection == 'W':
                list_moves.append('L')
            elif curdirection == 'E':
                list_moves.append('R')
            curdirection = 'S'
    return list_moves, curdirection

def execute_moves(clientID, list_moves):
    for move in list_moves:
        if move == 'S':
            client.simxSynchronousTrigger(clientID)
            client.simxSynchronous(clientID, True)
            _, _, _, _, _ = client.simxCallScriptFunction(
                clientID,
                'remoteApiCommandServer',
                sim.sim_scripttype_childscript,
                'moveForward@ROBOT',
                [],
                [],
                [],
                bytearray(),
                sim.simx_opmode_oneshot_wait,
            )
        elif move == 'L':
            _, _, _, _, _ = client.simxCallScriptFunction(
                clientID,
                'remoteApiCommandServer',
                sim.sim_scripttype_childscript,
                'turnLeft@ROBOT',
                [],
                [],
                [],
                bytearray(),
                sim.simx_opmode_oneshot_wait,
            )
        elif move == 'R':
            _, _, _, _, _ = client.simxCallScriptFunction(
                clientID,
                'remoteApiCommandServer',
                sim.sim_scripttype_childscript,
                'turnRight@ROBOT',
                [],
                [],
                [],
                bytearray(),
                sim.simx_opmode_oneshot_wait,
            )
        elif move == 'v':
            _, _, _, _, _ = client.simxCallScriptFunction(
                clientID,
                'remoteApiCommandServer',
                sim.sim_scripttype_childscript,
                'turnAround@ROBOT',
                [],
                [],
                [],
                bytearray(),
                sim.simx_opmode_oneshot_wait,
            )
        elif move == 'M':
            _, _, _, _, _ = client.simxCallScriptFunction(
                clientID,
                'remoteApiCommandServer',
                sim.sim_scripttype_childscript,
                'moveForwardMedium@ROBOT',
                [],
                [],
                [],
                bytearray(),
                sim.simx_opmode_oneshot_wait,
            )
    client.simxSynchronousTrigger(clientID)
    client.simxSynchronous(clientID, True)

def barcode_detection(image, visualize=False):
    decoded_objects = decode(image)
    for obj in decoded_objects:
        if visualize:
            points = obj.polygon
            if len(points) == 4:
                hull = cv2.convexHull(np.array([point for point in points], dtype=np.float32))
                cv2.polylines(image, [hull], True, (0, 255, 0), 2)
            else:
                print(f"Detected QR code with {len(points)} points.")
        data = obj.data.decode("utf-8")
        print(f"Decoded Data: {data}")
        return data

def main():
    sim.simxFinish(-1)
    clientID = sim.simxStart('127.0.0.1', 19997, True, True, 5000, 5)
    if clientID != -1:
        print('Connected to remote API server')

        start_node = 'A1'
        end_node = 'F6'

        path = path_planning(graph, start_node, end_node)
        moves, direction = paths_to_moves(path, 'N')

        # Execute the moves
        execute_moves(clientID, moves)

        # Capture image from the robot's camera
        _, resolution, image = client.simxGetVisionSensorImage(
            clientID,
            sim.simxGetObjectHandle(clientID, 'Vision_sensor', sim.simx_opmode_oneshot_wait)[1],
            0,
            sim.simx_opmode_oneshot_wait,
        )

        # Decode QR code from the captured image
        barcode_data = barcode_detection(image, visualize=True)

        print('Task completed')
    else:
        print('Failed connecting to remote API server')

    sim.simxFinish(clientID)

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
