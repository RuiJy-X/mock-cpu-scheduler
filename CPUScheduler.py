from collections import deque
import itertools
from collections import deque
import itertools
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from tabulate import tabulate

counter = itertools.count()
counter2 = itertools.count()

next(counter)
def new_process():
    return f"p{next(counter)}"

class CPUScheduler():
    def __init__(self):
        self.process = {} # {"process1": [5,2]} index 0 = burst time, index 1 = arrival time
        self.ready = deque() #contains all ready processes
        self.gantt = [] #{"p1": [start,end]} or [{"name": process name, "start": start, "end": end, "duration": duration}]
        self.in_queue = set() #filtering for ready queue
        self.current_process = None
        self.finished_process_summary = None
        self.display_process = None
        
    def display(self):
        print(f"Process\tBurst Time\tArrival Time")
        for processes,time in self.display_process.items():
            print(f"{processes}\t{time[0]}\t\t{time[1]}")
                   

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
        
    def print_gantt_chart(self):
        
        # Convert to DataFrame for easier handling
        df = pd.DataFrame(self.gantt)

        # 2. Setup the plot
        fig, ax = plt.subplots(figsize=(12, 4)) # Adjusted height since we only have one bar

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
        ax.set_title('Single-Processor Execution Timeline')
        
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
    