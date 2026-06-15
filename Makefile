CXX = clang++
CXXFLAGS = -std=c++17 -O2 -Wall -Wextra -fPIC -I cpp/include
PYTHON = python3
PYBIND11_INCLUDE = $(shell $(PYTHON) -m pybind11 --includes)
PYBIND11_SUFFIX = $(shell $(PYTHON) -c "import pybind11; print(pybind11.get_suffix())")

BUILD_DIR = build
SRC_DIR = cpp/src
INC_DIR = cpp/include

SOURCES = $(SRC_DIR)/match_engine.cpp \
          $(SRC_DIR)/club_ai.cpp \
          $(SRC_DIR)/stat_calculator.cpp \
          $(SRC_DIR)/bindings.cpp

TARGET = $(BUILD_DIR)/game_core$(PYBIND11_SUFFIX)

.PHONY: all clean run build

all: build

build: $(TARGET)

$(TARGET): $(SOURCES) | $(BUILD_DIR)
	$(CXX) $(CXXFLAGS) $(PYBIND11_INCLUDE) -shared $(SOURCES) -o $@

$(BUILD_DIR):
	mkdir -p $(BUILD_DIR)

clean:
	rm -rf $(BUILD_DIR)

run: build
	$(PYTHON) main.py

test: build
	$(PYTHON) -m pytest cpp/tests/ -v
