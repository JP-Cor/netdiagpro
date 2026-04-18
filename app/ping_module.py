import subprocess


def start_ping_process(host: str, count: int, size: int):
    cmd = ["ping", host, "-n", str(count), "-l", str(size)]

    process = subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        shell=True
    )
    return process


def read_ping_output(process, total_count: int, progress_callback=None, stop_callback=None) -> str:
    output_lines = []
    replies = 0

    for line in process.stdout:
        if stop_callback and stop_callback():
            try:
                process.terminate()
            except Exception:
                pass
            break

        output_lines.append(line)

        line_lower = line.lower()
        if "ttl=" in line_lower:
            replies += 1
            if progress_callback:
                progress_callback(replies, total_count)

    return "".join(output_lines)