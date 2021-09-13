import subprocess
import matplotlib.pyplot as plt
import pandas as pd

def traceroute(server, max_hops=30, timeout=10):
	
	i=0;

	server_list = []

	while(i<max_hops):
		
		# pinging the server provided with increasing ttl values each time
		# using flags:
		# 	-c 1			for a single ping attempt
		#		-t i 			to control the ttl
		#		-n 				to get an output which only contains the ip address of the server at last hop
		
		i = i+1
		ping_res = str(subprocess.Popen(["ping", "-c 1", f"-t {i}", f"-W {timeout}", "-n", server], stdout = subprocess.PIPE).communicate())

		# Only when the server at last hop is responding with a time limit exceeded message, the second
		# line of the output is "From <ip address of server> icmp_seq=1 Time to live exceeded"
		
		# I use a value of atleast len(server) + 30 as the second argument for all find calls to the 
		# ping_res so as to avoid any matches to any substring with the server name

		tmp = ping_res.find("From", len(server) + 30)
		
		if(tmp == -1):

			# either the server did not respond or we reached the destination host
			if(ping_res.find("1 received") != -1):
			
				# if a packet is received back successfully, it means that we have reached the destination host
				# getting the ip and rtt and pushing it onto the server list

				tmp = ping_res.find("from", len(server) + 30)
				ip = ping_res[tmp+5 : ping_res.find(" ", tmp+5)]

				tmp = ping_res.find("time", len(server) + 30)
				time = ping_res[tmp+5 : ping_res.find(" ", tmp+1)]

				print(f"IP : {ip}    hops to this server : {i}    round_trip_time : {time}")

				server_list.append((ip, i, float(time)))

				break
			
			else:

				server_list.append((" ", i, float(0)))
				print("This server does not respond")

		else:
			
			# When a server at last hop is responding, we take it's ip from the response to the ping command
			# and execute another ping onto this ip to get the rtt from our device to this server

			ip = ping_res[tmp+5 : ping_res.find(" ", tmp+5)]
			router_ping_res = str(subprocess.Popen(["ping", "-c 1", "-n", ip], stdout = subprocess.PIPE).communicate())

			tmp = router_ping_res.find("time", len(ip) + 30)
			time = router_ping_res[tmp+5 : router_ping_res.find(" ", tmp+1)]

			print(f"IP : {ip}    hops to this server : {i}    round_trip_time : {time}")

			server_list.append((ip, i, float(time)))

	# plotting a scatter plot of the rtt vs hops data 
	if(server_list != []):
		server_data = pd.DataFrame(server_list, columns = ['ip', 'hop', 'rtt'])
		plt.scatter(server_data['hop'], server_data['rtt'])
		plt.title(f'RTT vs Hop graph for {server}')
		plt.xlabel("Hops")
		plt.ylabel("RTT")
		plt.savefig(f'{server}_tracerout_graph.jpeg')
		plt.show()

if __name__ == '__main__':

	# taking input from the user
	server = input("Enter server name or ip: ")
	input_hops = input("Enter maximum number of permitted (leave blank for default of 30 hops): ")
	input_timeout = input("Enter the maximum time (in seconds) to wait for response from a server (leave blank for a default value of 10): ")

	max_hops = 30
	timeout = 10

	if(input_hops != ''):
		max_hops = int(input_hops)

	if(input_timeout != ''):
		timeout = input_timeout

	if(server == ''):

		# if no url is mentioned then the user is prompted with an error message
		print("Please enter a valid server or ip")
	else:

		# run traceroute on the given inputs
		traceroute(server, max_hops, timeout)