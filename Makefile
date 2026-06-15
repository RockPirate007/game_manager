CXX = clang++
CXXFLAGS = -std=c++17 -O2 -Wall -Wextra -fPIC -I cpp/include
PYTHON = python3

BUILD_DIR = build
SRC_DIR = cpp/src
INC_DIR = cpp/include

SOURCES = $(SRC_DIR)/match_engine.cpp \
          $(SRC_DIR)/club_ai.cpp \
          $(SRC_DIR)/stat_calculator.cpp \
          $(SRC_DIR)/bindings.cpp

.PHONY: all clean run cpp

all: cpp

cpp: $(SOURCES) | $(BUILD_DIR)
	@echo "Checking pybind11..."
	@$(PYTHON) -c "import pybind11" 2>/dev/null || { echo "pybind11 не установлен. Установите: pip install pybind11"; exit 1; }
	@echo "Checking clang++..."
	@which $(CXX) >/dev/null 2>&1 || { echo "clang++ не найден. Установите: pkg install clang"; exit 1; }
	@SUFFIX=$$($(PYTHON) -c "import pybind11; print(pybind11.get_suffix())" 2>/dev/null); \
	INCLUDES=$$($(PYTHON) -m pybind11 --includes 2>/dev/null); \
	echo "Сборка game_core$$SUFFIX..."; \
	$(CXX) $(CXXFLAGS) $$INCLUDES -shared $(SOURCES) -o $(BUILD_DIR)/game_core$$SUFFIX && \
	echo "C++ модуль собран успешно!"

$(BUILD_DIR):
	mkdir -p $(BUILD_DIR)

clean:
	rm -rf $(BUILD_DIR)

run: cpp
	$(PYTHON) main.py

run-python:
	$(PYTHON) main.py
