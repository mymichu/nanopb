import os

from conans import CMake, ConanFile, tools
from conans.errors import ConanInvalidConfiguration


class NanopbTestPackage(ConanFile):
    description = "TODO"
    generators = "cmake"
    settings = "arch", "compiler"
    exports_sources = "include/*", "src/*", "test/*", "CMakeLists.txt", ".parasoft_settings/*"

    def package(self):
        self.copy("include/*.h", dst="include", keep_path=False)
        self.copy("*.a", dst="lib", keep_path=False)

    def cmake_set_definitions(self, cmake):
        if self.settings.arch == "armv7" and self.settings.compiler == "gcc" :
            cmake.definitions["CMAKE_TRY_COMPILE_TARGET_TYPE"]=  "STATIC_LIBRARY"

    def cmake_configure_build(self, cmake):
        cmake.configure()
        cmake.build()

    def build(self):
        cmake = CMake(self)
        self.cmake_set_definitions(cmake)
        self.cmake_configure_build(cmake)

    def test(self):
        if not tools.cross_building(self.settings):
            bin_path = os.path.join("bin", "NanopbTest")
            self.run(bin_path, run_environment=True)