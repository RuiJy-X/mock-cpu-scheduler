from collections import deque
import itertools
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from tabulate import tabulate
from CPUScheduler import CPUScheduler
counter = itertools.count()
counter2 = itertools.count()

next(counter)
def new_process():
    return f"p{next(counter)}"

class RoundRobin(CPUScheduler):
    def __init__(self,time_quantum):
        self.process = {} # {"process1": [5,2]} index 0 = burst time, index 1 = arrival time
        self.ready = deque() #contains all ready processes
        self.gantt = [] #{"p1": [start,end]} or [{"name": process name, "start": start, "end": end, "duration": duration}]
        self.in_queue = set() #filtering for ready queue
        self.current_process = None
        self.finished_process_summary = None
        self.display_process = None
        self.time_quantum = time_quantum
        
    def __str__(self):
        return "Round Robin"
    def input_process(self,burst_time, arrival_time):
        """_summary_

        Args:
            burst_time (_int_): The time duration when the process will finish
            arrival_time (_int_): The time that the process will be inserted at the ready queue 
        """
        self.process[new_process()] = [burst_time,arrival_time] #create new process (p0,p1,p2..pn) with : [burst_time,arrival_time]
        self.display_process = self.process.copy()
    
    def display(self):
        print(f"Process\tBurst Time\tArrival Time")
        for processes,time in self.display_process.items():
            print(f"{processes}\t{time[0]}\t\t{time[1]}")
       
            
    def insert_ready(self,current_time):
        """_summary_

        Args:
            current_time (_int_): Is the current accumulative time of each process. Calculated using  where if PxBT = process burst time of x process, then current time = P1BT + ... PnBT 
            
        First the function sorts the processes by arrival time
        Then it checks which process was last added to the ready queue and transfers it to the last index of the sorted list of procesess
        
        Next it iterates that list then extract the arrival time and burst time
        If the arrival time of the current process is less than the current time and,
        if it still has a remaining burst time and; 
        the process is not already in the queue
        then append the process to the ready queue and in the in_queue filtering set.
        """
        #given the current time, find the next process to be appended to the queue
        
        sorted_arrivals = sorted(self.process.items(),key=lambda item: (item[1][1], item[0]))
        
        for i in sorted_arrivals:
            if i[0] == self.current_process:
                sorted_arrivals.remove(i)
                sorted_arrivals.append(i)
        
        for p, time in sorted_arrivals:
            arrival_time = time[1]
            burst_time = time[0]
            if (arrival_time <= current_time and burst_time > 0 and p not in self.in_queue):
                # print(f"preempting {p} arrival time {arrival_time}, at {current_time}")
                self.ready.append(p)
                self.in_queue.add(p)
                

    def get_key(self,value):
        for p,t in self.process.items():
            if t[1] == value:
                return p 
            
    def has_remaining_burst(self):
        for time in self.process.values():
            burst_time = time[0]
    
            if burst_time > 0:
                return True

        return False
    
    def get_next_arrival_time(self, current_burst_time):
        """_summary_

        Args:
            current_burst_time (_int_): curent burst time

        Returns:
            _object_: process
            
        This is a skip ahead mechanism, it checks the current burst time and returns the next arrival time  
        The returned arrival time will be used to change the current burst time in the main iteration
        """
        sorted_arrivals = sorted(self.process.items(),key=lambda item: (item[1][1], item[0]))
        
        for p,time in sorted_arrivals:
            arrival_time = time[1]

            
            if arrival_time >= current_burst_time:
                return arrival_time
    
    def is_idle(self):
        """_summary_
        Checks if cpu the idle or has no processes running
        if there are no processes in the ready queue, that means its idle
        """
        if not self.ready:
            return True
        else:
            return False
                    
    def schedule(self):
        #what makes the algorithm loop?
        #Check which processes can be inserted to the ready queue
        #while ready queue?
        #then insert processes in the ready queue to the gantt chart
        #Check which processes can be inserted to the ready queue
        
        #Start with setting the initial burst time to 0 and insert processes that are ready for insertion
        burst_time = 0
        self.insert_ready(burst_time)
        
        while self.ready or self.has_remaining_burst():
            
            if self.is_idle():
                #Skips ahead to the time where there is a process to be added
                new_time = self.get_next_arrival_time(burst_time)
                
                
                start = burst_time
                end = new_time
                duration = end - start
                
                self.gantt.append({"process_name": "IDLE", "start":start,"end": end,"duration": duration,"arrival_time":process_arrival_time})
                
                burst_time = new_time
                self.insert_ready(burst_time)
                continue
            
            process = self.ready.popleft() # get process in the queue
            self.current_process = process #used to avoid requeuing the last process added as the first to the ready queue
            self.in_queue.remove(process)
            
            process_time = self.process.get(process) #get process time, returns [burst_time,arrival_time]
            process_burst_time = process_time[0]
            process_arrival_time = process_time[1]
            
            
            time_slice = min(self.time_quantum, process_burst_time) #if burst time is lower, it chooses that, else take time quantum
            burst_left = process_burst_time - time_slice # subtract burst time with time quantum, used for updating remaining burst time
            
            if burst_left < 0: #if its less than 0 just make it 0 to avoid negatives
                burst_left = 0
                
            #update process dict with the remaning burst time
            self.process[process]= [burst_left,process_arrival_time]
             
            # burst time is the current time of the gantt chart basically
            
            start = burst_time
            end = burst_time + time_slice

            self.gantt.append({"process_name": process,"start":start,"end":end,"duration":time_slice,"arrival_time":process_arrival_time})
            #set the current time (which is called burst time in this case) to the end.
            
            burst_time = end
            self.insert_ready(end)

        return self.gantt
            

    def get_waiting_times(self):
        """
        Calculates the waiting time and average waiting time for all processes.
        WT = Turnaround Time - Total Burst Time
        """
        
        df = pd.DataFrame(self.gantt)
      
        # 1. Group by process name to calculate total burst time and completion time
        process_summary = df.groupby('process_name').agg(
            # Total Burst Time (BT) is the sum of all execution durations
            Total_Burst_Time=('duration', 'sum'),
            # Completion Time (CT) is the time of the last segment's end
            Completion_Time=('end', 'max'),
            Arrival_Time = ("arrival_time","max")
        ).reset_index()

        # 2. Calculate Turnaround Time (TAT)
        # TAT = Completion Time - Arrival Time (assuming Arrival Time = 0)
        process_summary['Turnaround_Time'] = process_summary['Completion_Time'] 
        
        # 3. Calculate Waiting Time (WT)
        # WT = TAT - Total Burst Time
        process_summary['Waiting_Time'] = process_summary['Turnaround_Time'] - process_summary['Total_Burst_Time'] - process_summary["Arrival_Time"]
        
        self.finished_process_summary = process_summary[["process_name","Total_Burst_Time","Arrival_Time","Waiting_Time"]].set_index("process_name")
        print(tabulate(self.finished_process_summary,headers = "keys",tablefmt="grid"))
        return tabulate(self.finished_process_summary,headers = "keys",tablefmt="grid")
    
    def average_waiting_time(self):
        avg_wt_time = self.finished_process_summary.loc[:,"Waiting_Time"].sum() / self.finished_process_summary.loc[:,"Waiting_Time"].count()
        
        print("Average Waiting Time: ",end="")
        print(avg_wt_time)
        
        return avg_wt_time
    
        

            
    def print_gantt_chart(self):
        
        # Convert to DataFrame for easier handling
        df = pd.DataFrame(self.gantt)
        summary_df = self.finished_process_summary
        avg_wt = self.average_waiting_time() # Calculate Average WT
        

        # 2. Setup the plot
        fig, (ax_table,ax) = plt.subplots(2,1,figsize=(12, 8),gridspec_kw={'height_ratios': [1.5, 1], 'hspace': 0.1}) # Adjusted height since we only have one bar

        ax_table.set_title(f'Round Robin Scheduling (Q={self.time_quantum}) Performance Summary', pad=7, fontweight='bold')
        
        # Create the table on the top subplot (ax_table)
        table = ax_table.table(
            cellText=summary_df.values, 
            colLabels=["Total Burst Time (ms)", "Arrival Time (ms)", "Waiting time (ms)"], 
            rowLabels=summary_df.index,
            cellLoc='center', 
            loc='center'
        )
        
        table.auto_set_font_size(False)
        table.set_fontsize(10)
        table.scale(1.2, 1.5) # Scale the table for better visibility
        
        ax_table.text(
            0.5, # X position (0.5 is center)
            0.1, # Y position (0.1 is close to the bottom)
            f"Average Waiting Time: {avg_wt:.2f}ms", 
            transform=ax_table.transAxes, # Use axes coordinates
            ha='center', 
            va='center', 
            fontsize=12,
            fontweight='bold',
            color='darkred'
        )
        
        # Hide the axes for the table subplot
        ax_table.axis('off')
        ax_table.set_xticks([])
        ax_table.set_yticks([])
        
        # Get unique processes to assign unique colors
        unique_processes = df['process_name'].unique()
        unique_processes.sort()
        
        # Generate a color map based on number of unique processes
        colors = plt.cm.Set2(np.linspace(0, 1, len(unique_processes)))
        color_dict = dict(zip(unique_processes, colors))
        
        # 3. Plot the bars
        # Matplotlib's barh takes: y, width (duration), left (start time)
        # We use y=0 for all bars to place them on the same horizontal line
        for i, row in df.iterrows():
            ax.barh(
                y=0, 
                width=row['duration'], 
                left=row['start'], 
                color=color_dict[row['process_name']],
                edgecolor='black',
                height=0.4, # Make the bar slightly thinner/nicer looking
                alpha=0.8
            )
            
            # Add text inside the bars (Process Name)
            center_x = row['start'] + (row['duration'] / 2)
            ax.text(
                center_x, 
                0, 
                f"{row['process_name']}", 
                ha='center', 
                va='center', 
                color='black',
                fontweight='bold'
            )

        # 4. Formatting the Chart
        ax.set_xlabel('Time Units')
        ax.set_title('Round Robin Gantt Chart')
        
        # Set X-axis ticks to match the exact start/end points
        all_ticks = sorted(list(set(df['start'].tolist() + df['end'].tolist())))
        ax.set_xticks(all_ticks)
        
        # Clean up Y-axis
        ax.set_yticks([])     # Remove y-axis ticks
        ax.set_ylim(-0.5, 0.5) # Center the single bar vertically
        
        # Add gridlines on x-axis
        ax.grid(axis='x', linestyle='--', alpha=0.7)

        # Show the plot
        plt.tight_layout()
        plt.show()
        
    def get_all(self):
        self.display()
        print("\n")
        self.get_waiting_times()
        print("\n")
        self.average_waiting_time()
        print("\n")
        self.print_gantt_chart()
    

        
def main():
    rr = RoundRobin(time_quantum=2)
    rr.input_process(4,0)
    rr.input_process(2,2)
    rr.input_process(5,4)
    rr.input_process(3,1)
    rr.schedule()
    rr.get_all()
    
if __name__ == "__main__":
    main()
    
    