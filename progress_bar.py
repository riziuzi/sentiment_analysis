import sys
import time

class Progress:
        neon_colors = ['\033[38;5;196m', '\033[38;5;202m', '\033[38;5;208m', '\033[38;5;214m', '\033[38;5;220m',
                        '\033[38;5;226m', '\033[38;5;190m', '\033[38;5;154m', '\033[38;5;118m', '\033[38;5;82m',
                        '\033[38;5;46m', '\033[38;5;48m', '\033[38;5;50m', '\033[38;5;82m', '\033[38;5;118m',
                        '\033[38;5;154m', '\033[38;5;190m', '\033[38;5;226m', '\033[38;5;220m', '\033[38;5;214m',
                        '\033[38;5;208m', '\033[38;5;202m', '\033[38;5;196m', '\033[38;5;160m', '\033[38;5;124m',
                        '\033[38;5;88m', '\033[38;5;52m', '\033[38;5;53m', '\033[38;5;54m', '\033[38;5;55m',
                        '\033[38;5;56m', '\033[38;5;57m', '\033[38;5;58m', '\033[38;5;59m', '\033[38;5;60m',
                        '\033[38;5;61m', '\033[38;5;62m', '\033[38;5;63m', '\033[38;5;64m', '\033[38;5;65m',
                        '\033[38;5;66m', '\033[38;5;67m', '\033[38;5;68m', '\033[38;5;69m', '\033[38;5;70m',
                        '\033[38;5;71m', '\033[38;5;72m', '\033[38;5;73m', '\033[38;5;74m', '\033[38;5;75m']

        def __init__(self, total_iterations):
            self.total_iterations = total_iterations  # Total number of iterations
            self.pbar_length = 40  # Length of the moving line
            self.start_time = time.time()
            self.previous_time = self.start_time
            self.i = 0
            self.symbol = "-"
        # ANSI escape sequences for neon colors

        # Simulate the moving line

        def update(self,increment):
            current_color = Progress.neon_colors[self.i % len(Progress.neon_colors)]
            line_progress = int((self.i + 1) / self.total_iterations * self.pbar_length)
            line = current_color + self.symbol * line_progress

            # Format progress information
            progress = f'{self.i+1}/{self.total_iterations}'


            elapsed_time = time.time() - self.previous_time
            try:
                speed = f'{1 / elapsed_time:.2f} itr/s'
            except Exception:
                speed = f'0.00 itr/s'

            elapsed_time = time.time() - self.start_time
            average_time_per_item = elapsed_time / (self.i+1)

            # Calculate remaining time and ETA
            remaining_items = self.total_iterations - self.i-1
            remaining_time = remaining_items * average_time_per_item
            eta = time.strftime("%H:%M:%S", time.gmtime(remaining_time))

            # Calculate the width of the available space for progress information
            space_width = max(0, self.pbar_length - line_progress - len(progress) - len(speed) - len(eta) +28)

            # Clear previous output and print the moving line and progress information
            sys.stdout.write('\r')
            sys.stdout.write(f'{line} {" " * space_width} {progress} {speed} eta {eta}')
            sys.stdout.flush()
            self.previous_time = time.time()
            self.i+=increment
            if(self.i==self.total_iterations):
                sys.stdout.write('\n')
            
        def start(self):
            self.update(0)

        

# Call the animate_neon_line function


if __name__ == '__main__':
    iterations = 113
    pbar = Progress(total_iterations=iterations)
    print("\n       Starting process number 001897.kt5\n")
    for i in range(iterations):
        pbar.update(1)
        time.sleep(0.2)
    print("     Success!\n Followup process starts now!")
    pbar2 = Progress(total_iterations=iterations)
    for i in range(iterations):
        pbar2.update(1)
        time.sleep(0.01)
        
    print("\n       Success!\n")
