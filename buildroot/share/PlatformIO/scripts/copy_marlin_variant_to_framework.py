import os,shutil
from SCons.Script import DefaultEnvironment
from platformio import util
try:
    # PIO < 4.4
    from platformio.managers.package import PackageManager
except ImportError:
    # PIO >= 4.4
    from platformio.package.meta import PackageSpec as PackageManager

def parse_pkg_uri(spec):
    if PackageManager.__name__ == 'PackageSpec':
        return PackageManager(spec).name
    else:
        name, _, _ = PackageManager.parse_pkg_uri(spec)
        return name

def copytree(src, dst, symlinks=False, ignore=None):
    for item in os.listdir(src):
        s = os.path.join(src, item)
        d = os.path.join(dst, item)
        if os.path.isdir(s):
            shutil.copytree(s, d, symlinks, ignore)
        else:
            shutil.copy2(s, d)

env = DefaultEnvironment()
platform = env.PioPlatform()
board = env.BoardConfig()
variant = board.get("build.variant")
variant_dir = ' +<buildroot/share/PlatformIO/variants/' + variant + '>';
src_filter = env.get("SRC_FILTER")
print("Starting SRC Filter:", env.get("SRC_FILTER"))
src_filter_value = src_filter[0];

src_filter_value = src_filter_value + variant_dir
src_filter[0] = src_filter_value;
env["SRC_FILTER"] = src_filter

print("Modified SRC Filter:", env.get("SRC_FILTER"))

cxx_flags = env['CXXFLAGS']
print("CXXFLAGS", cxx_flags)

platform_packages = env.GetProjectOption('platform_packages')
# if there's no framework defined, take it from the class name of platform
framewords = {
    "Ststm32Platform": "framework-arduinoststm32",
    "AtmelavrPlatform": "framework-arduino-avr"
}
if len(platform_packages) == 0:
    platform_name = framewords[platform.__class__.__name__]
else:
    platform_name = parse_pkg_uri(platform_packages[0])

FRAMEWORK_DIR = platform.get_package_dir(platform_name)
assert os.path.isdir(FRAMEWORK_DIR)
assert os.path.isdir("buildroot/share/PlatformIO/variants")

variant_dir = os.path.join(FRAMEWORK_DIR, "variants", variant)

source_dir = os.path.join("buildroot/share/PlatformIO/variants", variant)
assert os.path.isdir(source_dir)

if os.path.isdir(variant_dir):
    shutil.rmtree(variant_dir)

if not os.path.isdir(variant_dir):
    os.mkdir(variant_dir)

copytree(source_dir, variant_dir)
