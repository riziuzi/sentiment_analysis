import sys
import time

def animate_neon_line():
    total_iterations = 1000  # Total number of iterations
    line_length = 40  # Length of the moving line
    start_time = time.time()

    # ANSI escape sequences for neon colors
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

    # Simulate the moving line
    for i in range(total_iterations):
        current_color = neon_colors[i % len(neon_colors)]
        line_progress = int((i + 1) / total_iterations * line_length)
        line = current_color + '-' * line_progress

        # Format progress information
        progress = f'{i+1}/{total_iterations}'


        elapsed_time = time.time() - start_time
        try:
            speed = f'{float(line_length) / elapsed_time* 2:.2f} itr/s'
        except:
            speed = f'0.00 itr/s'

        elapsed_time = time.time() - start_time
        average_time_per_item = elapsed_time / (i+1)

        # Calculate remaining time and ETA
        remaining_items = total_iterations - i-1
        remaining_time = remaining_items * average_time_per_item
        eta = time.strftime("%H:%M:%S", time.gmtime(remaining_time))

        # Calculate the width of the available space for progress information
        space_width = max(0, line_length - line_progress - len(progress) - len(speed) - len(eta) +28)

        # Clear previous output and print the moving line and progress information
        sys.stdout.write('\r')
        sys.stdout.write(f'{line} {" " * space_width} {progress} {speed} eta {eta}')
        sys.stdout.flush()

        time.sleep(.01)  # Adjust the speed of the moving line

    sys.stdout.write('\n')

# Call the animate_neon_line function


if __name__ == '__main__':
    animate_neon_line(total_iterations=1000)
