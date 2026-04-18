import subprocess


def get_full_network_info() -> str:
    commands = [
        "ipconfig /all",
        "getmac /v"
    ]

    output = []
    output.append("========== INFORMACION COMPLETA DE RED ==========\n")

    for cmd in commands:
        output.append(f"\n===== COMANDO: {cmd} =====\n")
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            shell=True
        )

        if result.stdout:
            output.append(result.stdout)
        if result.stderr:
            output.append("\n[ERRORES]\n")
            output.append(result.stderr)

    return "\n".join(output)