import sys

def progress_bar(current, total):
    """
    Displays a progress bar that updates dynamically.
    """
    bar_length = 40
    percent = 100.0 * current / total
    sys.stdout.write('\r')
    progress = int(bar_length * current / total)
    sys.stdout.write("Progression Moyenne : {:.2f}% [".format(percent) + "█" * progress + " " * (bar_length - progress) + "]")
    sys.stdout.flush()
    if current == total:
        print()
