import argparse
import os
import shutil
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TERRAFORM_DIR = ROOT / "terraform"

DEFAULTS = {
    "RESOURCE_GROUP_NAME": None,
    "RESOURCE_GROUP_NAME_PREFIX": "rg-mlops-cancer",
    "LOCATION": "eastus2",
}


def run(cmd, cwd=None):
    print("\n$ " + " ".join(cmd))
    subprocess.check_call(cmd, cwd=cwd)


def hcl_value(value):
    if value is None:
        return "null"
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, (int, float)):
        return str(value)
    if isinstance(value, (list, tuple)):
        rendered = ", ".join(hcl_value(item) for item in value)
        return f"[{rendered}]"
    escaped = str(value).replace("\"", "\\\"")
    return f"\"{escaped}\""


def write_tfvars(path, items):
    lines = [f"{key} = {hcl_value(value)}" for key, value in items]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def load_env_file(path):
    if not path.exists():
        return
    for line in path.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#") or "=" not in stripped:
            continue
        key, value = stripped.split("=", 1)
        key = key.strip()
        value = value.strip()
        if key and key not in os.environ:
            os.environ[key] = value


def env_or_default(key, default):
    value = os.environ.get(key)
    if value is None:
        return default
    if value.strip() == "" or value.strip().lower() == "null":
        return None
    return value


def get_terraform_exe():
    env_path = os.environ.get("TERRAFORM_EXE")
    if env_path:
        return env_path
    exe = shutil.which("terraform")
    if not exe:
        raise RuntimeError("terraform not found on PATH. Set TERRAFORM_EXE or install Terraform.")
    exe_lower = exe.lower()
    if exe_lower.endswith(r"\chocolatey\bin\terraform.exe"):
        candidate = r"C:\ProgramData\chocolatey\lib\terraform\tools\terraform.exe"
        if Path(candidate).exists():
            return candidate
    return exe


def write_resource_group_tfvars():
    rg_dir = TERRAFORM_DIR / "01_resource_group"
    write_tfvars(
        rg_dir / "terraform.tfvars",
        [
            ("resource_group_name", env_or_default("RESOURCE_GROUP_NAME", DEFAULTS["RESOURCE_GROUP_NAME"])),
            ("resource_group_name_prefix", env_or_default("RESOURCE_GROUP_NAME_PREFIX", DEFAULTS["RESOURCE_GROUP_NAME_PREFIX"])),
            ("location", env_or_default("LOCATION", DEFAULTS["LOCATION"])),
        ],
    )


def terraform_destroy(module_dir):
    terraform_exe = get_terraform_exe()
    run([terraform_exe, "init", "-upgrade"], cwd=module_dir)
    run([terraform_exe, "destroy", "-auto-approve"], cwd=module_dir)


def cleanup_outputs(module_dir):
    outputs_path = module_dir / "outputs.json"
    if outputs_path.exists():
        outputs_path.unlink()


def main():
    parser = argparse.ArgumentParser(description="Destroy Terraform resources for the MLOps project.")
    parser.add_argument("--rg-only", action="store_true", help="Destroy only the resource group")
    args = parser.parse_args()

    load_env_file(ROOT / ".env")

    modules = [TERRAFORM_DIR / "01_resource_group"]
    if args.rg_only:
        modules = [TERRAFORM_DIR / "01_resource_group"]

    write_resource_group_tfvars()

    for module_dir in modules:
        terraform_destroy(module_dir)
        cleanup_outputs(module_dir)


if __name__ == "__main__":
    main()
