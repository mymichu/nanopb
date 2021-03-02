from conans import ConanFile, CMake, tools
from conans.errors import ConanInvalidConfiguration
import os
import stat
import shutil
import pip
from os import path

protobuf_version="3.14.0"
class NanoPbConan(ConanFile):
    name = "nanopb"
    license = "zlib"
    url = "https://jpa.kapsi.fi/nanopb/"
    description = "Protocol Buffers with small code size"
    settings = "os", "arch", "compiler", "build_type"
    generators = "cmake"
    exports = '*'
    keep_imports = True
    options = {
        "static_libs": [True, False],
        "shared_libs": [True, False],
        "runtime": [True, False],
        "generator": [True, False],
        "msvc_static_libs": [True, False]
    }
    default_options = {
        "static_libs": True,
        "shared_libs":  False,
        "runtime": True,
        "generator":  True,
        "msvc_static_libs": False
    }

    def getBuildOS(self):
        os = self.settings.os
        if tools.cross_building(self):
            if hasattr(self,"settings_build"):
                os = self.settings_build.os
            else:
                os = self.settings.os
        return os
    
    def getBuildArch(self):
        arch = self.settings.arch
        if tools.cross_building(self):
            if hasattr(self,"settings_build"):
                arch = self.settings_build.arch
            else:
                arch = "x86_64"
        return arch

    def getTargetArch(self):
        arch = self.settings.arch
        if tools.cross_building(self):
            if hasattr(self,"settings_target.arch"):
                arch = self.settings_target.arch
        return arch

    def checkInstallProtocSupport(self):
        build_os = self.getBuildOS()
        build_arch = self.getBuildArch()
        return True if build_os == "Linux" and self.options.generator and build_arch == "x86_64" or build_arch == "x86" else False
       

    def source(self):
        if self.checkInstallProtocSupport():
            build_arch = self.getBuildArch()
            if build_arch == "x86_64":
                protocurl = f"https://github.com/protocolbuffers/protobuf/releases/download/v{protobuf_version}/protoc-{protobuf_version}-linux-x86_64.zip"
            else:
                protocurl = f"https://github.com/protocolbuffers/protobuf/releases/download/v{protobuf_version}/protoc-{protobuf_version}-linux-x86_32.zip"
            tools.download(url=protocurl, filename="protoc.zip", overwrite=True)
            tools.unzip(filename="protoc.zip", destination="protoc")
            st = os.stat('protoc/bin/protoc')
            os.chmod('protoc/bin/protoc', st.st_mode | stat.S_IEXEC)
       
    def system_requirements(self):
        if self.checkInstallProtocSupport():
            pip.main(["install", f"protobuf=={protobuf_version}"])

    def configure(self):
        build_os = self.getBuildOS()
        if build_os == "Windows" and self.settings.compiler == "Visual Studio":
            del self.options.fPIC

    def configure_cmake(self):
        cmake = CMake(self)
        targetArch = self.getTargetArch()
        if targetArch == "armv7" and self.settings.compiler == "gcc" :
            cmake.definitions["CMAKE_TRY_COMPILE_TARGET_TYPE"]=  "STATIC_LIBRARY"
        cmake.definitions["BUILD_STATIC_LIBS"]=  self.options.static_libs
        cmake.definitions["BUILD_SHARED_LIBS"]=  self.options.shared_libs
        cmake.definitions["nanopb_BUILD_RUNTIME"]=  self.options.runtime
        cmake.definitions["nanopb_BUILD_GENERATOR"]=  self.options.generator
        cmake.definitions["nanopb_MSVC_STATIC_RUNTIME"]=  self.options.msvc_static_libs
        cmake.configure(source_folder=path.join(self.source_folder, "conan/wrapper"))
        return cmake

    def build(self):
        if self.checkInstallProtocSupport():
            os.environ["PATH"] += os.pathsep + f"{self.build_folder}/protoc/bin"
        cmake = self.configure_cmake()
        cmake.build()

    def find_proto_folder(self):
        for root, dirs, files in os.walk(f"{self.package_folder}/lib", topdown=False):
            for name in dirs:
                if "proto" in name:
                    return f"{root}/{name}"

    def package(self):
        self.copy("pb*.h", dst="include", keep_path=False)
        self.copy("lib/*.a", dst="lib", keep_path=False)
        if self.options.generator:
            self.copy("FindNanopb.cmake", src="extra" ,dst="cmake", keep_path=False)
            cmake = self.configure_cmake() 
            cmake.install()
            if self.checkInstallProtocSupport():
                self.copy("*", src="protoc/bin", dst="bin/protoc", keep_path=False)
                tools.patch(base_path=f"{self.package_folder}/cmake", patch_file=f"{self.source_folder}/conan/patch/FindNanopb.patch", strip=1)
                os.system(f"ls {self.package_folder}/lib/python3.7/site-packages")
                MAIN_DIR = f"{self.package_folder}/lib"
                name = "proto"
                proto_path = self.find_proto_folder()
                shutil.move(src=f"{proto_path}",dst=f"{self.package_folder}/bin")
                self.copy("*", src="protoc/include", dst=f"{self.package_folder}/bin/proto", keep_path=True)

    def package_info(self):
        if self.checkInstallProtocSupport():
            self.env_info.path.append(os.path.join(self.package_folder, "bin/protoc"))
        self.cpp_info.includedirs = ["include"]
        self.cpp_info.libdirs = ["lib"]
        self.cpp_info.builddirs.append("cmake")
        if self.settings.build_type == "Debug":
            self.cpp_info.libs = ["protobuf-nanopbd"]
        else:
            self.cpp_info.libs = ["protobuf-nanopb"]
        