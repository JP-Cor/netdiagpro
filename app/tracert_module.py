import subprocess


def start_tracert_process(host: str):
    cmd = ["tracert", host]

    process = subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        shell=True
    )
    return process


def read_tracert_output(process, stop_callback=None) -> str:
    output_lines = []

    for line in process.stdout:
        if stop_callback and stop_callback():
            try:
                process.terminate()
            except Exception:
                pass
            break

        output_lines.append(line)

    return "".join(output_lines)