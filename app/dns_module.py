import subprocess

def get_dns_info() -> str:
    result = subprocess.run(
        ["ipconfig", "/all"],
        capture_output=True,
        text=True,
        shell=True
    )
    return result.stdout if result.stdout else result.stderr

def set_dns(adapter_name: str, primary_dns: str, secondary_dns: str | None = None) -> str:
    commands = [
        f'netsh interface ip set dns name="{adapter_name}" static {primary_dns}'
    ]

    if secondary_dns:
        commands.append(
            f'netsh interface ip add dns name="{adapter_name}" {secondary_dns} index=2'
        )

    output = []
    for cmd in commands:
        result = subprocess.run(cmd, capture_output=True, text=True, shell=True)
        output.append(result.stdout if result.stdout else result.stderr)

    return "\n".join(output)

def reset_dns(adapter_name: str) -> str:
    cmd = f'netsh interface ip set dns name="{adapter_name}" dhcp'
    result = subprocess.run(cmd, capture_output=True, text=True, shell=True)
    return result.stdout if result.stdout else result.stderr