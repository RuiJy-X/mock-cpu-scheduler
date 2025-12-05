from Priority import Priority
from RoundRobin import RoundRobin

def get_int_input(prompt):
    """Keep asking until the user enters a valid integer."""
    while True:
        try:
            return int(input(prompt))
        except ValueError as e:
            print(f"Invalid input! Must be an integer. Error: {e}")

def main_menu():
    print("Choose CPU Scheduler:")
    print("[1] Round Robin\n[2] Priority\n")
    return get_int_input(">>> ")

def main():
    choice = main_menu()
    CPUScheduler = None

    if choice == 1:
        print("Pick a time quantum:")
        tq = get_int_input(">>> ")
        CPUScheduler = RoundRobin(time_quantum=tq)
    else:
        CPUScheduler = Priority()

    print(f"\nChosen Scheduler: {str(CPUScheduler)}\n")
    print("How many processes: ")
    process_size = get_int_input(">>> ")

    for i in range(1, process_size + 1):
        print(f"\nProcess {i}")

        # Each input has its own loop for error handling
        burst_time = get_int_input("Burst Time: >>> ")
        arrival_time = get_int_input("Arrival Time: >>> ")

        if str(CPUScheduler) == "Priority":
            priority = get_int_input("Priority: >>> ")
            CPUScheduler.input_process(burst_time, arrival_time, priority)
        else:
            CPUScheduler.input_process(burst_time, arrival_time)

    print("\nScheduling processes...\n")
    CPUScheduler.schedule()
    CPUScheduler.get_all()

if __name__ == "__main__":
    main()
    