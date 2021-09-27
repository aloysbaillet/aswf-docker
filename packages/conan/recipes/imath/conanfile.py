from conans import ConanFile, tools, CMake
import os

required_conan_version = ">=1.33.0"


class ImathConan(ConanFile):
    name = "imath"
    description = "Seamless operability between C++11 and Python"
    topics = "conan", "imath", "python", "binding"
    homepage = "https://www.qt.io/qt-for-python"
    license = "LGPL-3.0"
    url = "https://github.com/conan-io/conan-center-index"
    settings = (
        "os",
        "arch",
        "compiler",
        "build_type",
        "ci_common",
        "vfx_platform",
        "python",
    )
    generators = "cmake_find_package_multi"

    _cmake = None
    _source_subfolder = "source_subfolder"

    def requirements(self):
        self.requires(
            f"python/{os.environ['ASWF_PYTHON_VERSION']}@{self.user}/{self.channel}"
        )
        self.requires(f"boost/{os.environ['ASWF_BOOST_VERSION']}@{self.user}/{self.channel}")

    def build_requirements(self):
        self.build_requires(
            f"cmake/{os.environ['ASWF_CMAKE_VERSION']}@{self.user}/{self.channel}"
        )

    def source(self):
        tools.get(f"https://github.com/AcademySoftwareFoundation/Imath/archive/v{self.version}.tar.gz")
        os.rename(f"Imath-{self.version}", self._source_subfolder)

    def _configure_cmake(self):
        if self._cmake:
            return self._cmake

        with tools.environment_append(tools.RunEnvironment(self).vars):
            self._cmake = CMake(self)
            self._cmake.definitions["PYTHON"] = "ON"
            self._cmake.configure(source_folder=self._source_subfolder)
            return self._cmake

    def build(self):
        cmake = self._configure_cmake()
        cmake.build()

    def package(self):
        self.copy("LICENSE.md", src=self._source_subfolder, dst="licenses")
        cmake = self._configure_cmake()
        cmake.install()

    def package_info(self):
        self.cpp_info.requires.append("python::PythonLibs")
        self.cpp_info.requires.append("boost::python")
        pymajorminor = self.deps_user_info["python"].python_interp
        self.env_info.PYTHONPATH.append(
            os.path.join(self.package_folder, "lib", pymajorminor, "site-packages")
        )
        self.env_info.CMAKE_PREFIX_PATH = os.path.join(self.package_folder, "lib", "cmake")
