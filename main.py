from Priority import Priority
from RoundRobin import RoundRobin

def section_wrapper(func):
    def wrap():
        print("=========================================================")
        func()
        print("=========================================================")
        
    return wrap()


def main_menu():
    print("Choose CPU Scheduler:")
    print("[1] Round Robin\n[2] Priority\n")
    choose = int(input(">>> "))
    print()
    return choose



def main():
    choice = main_menu()
    CPUScheduler = None
    if choice == 1:
        print("Pick a time quantum:\n")
        tq = int(input(">>> "))
        CPUScheduler = RoundRobin(time_quantum= tq)
    else:
        CPUScheduler = Priority()
    print("\n")
    print(f"Chosen Scheduler:  {str(CPUScheduler)}\n")    
    print("How many processess: ")
    process_size = int(input(">>> "))
    print("\n")
    
    for i in range(1,process_size +1):
        print(f"Process {i}")
        print("Burst Time:")
        burst_time = int(input(">>> "))
        print("\n")
        print("Arrival Time: ")
        arrival_time = int(input(">>> "))
        print("\n")
        
        if str(CPUScheduler) == "Priority":
            print("Priority")
            priority = int(input(">>> "))
            
            print("\n")
            CPUScheduler.input_process(burst_time,arrival_time,priority)
        else:
            CPUScheduler.input_process(burst_time,arrival_time)
        
        
    CPUScheduler.schedule()
    CPUScheduler.get_all()
    
    pass

if __name__ == "__main__":
    main()
