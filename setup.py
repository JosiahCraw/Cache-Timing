from subprocess import PIPE, run

if __name__ == "__main__":
    packages = ["firebase_admin", "matplotlib", "py-cpuinfo", "Pillow"]
    for package in packages:
        cmd = 'pip3 install --user ' + package
        result = run(cmd, stdout=PIPE, stderr=PIPE, universal_newlines=True, shell=True)
        print(result.stderr)