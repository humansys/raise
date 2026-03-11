"""Tests for Dart/Flutter symbol extraction."""

from __future__ import annotations

from raise_cli.discovery.scanner import (
    detect_language,
    extract_dart_symbols,
    extract_symbols,
)

# ── Language detection ───────────────────────────────────────────────────


def test_detect_language_dart() -> None:
    assert detect_language("lib/main.dart") == "dart"


def test_detect_language_dart_nested() -> None:
    assert detect_language("lib/src/models/user.dart") == "dart"


# ── Dispatch ─────────────────────────────────────────────────────────────


def test_extract_symbols_dispatches_dart() -> None:
    source = "void main() {}"
    symbols = extract_symbols(source, "main.dart", "dart")
    assert len(symbols) >= 1
    assert symbols[0].name == "main"
    assert symbols[0].kind == "function"


# ── Classes ──────────────────────────────────────────────────────────────


def test_extract_class() -> None:
    source = """\
class UserService {
  void process() {}
}
"""
    symbols = extract_dart_symbols(source, "user_service.dart")
    classes = [s for s in symbols if s.kind == "class"]
    assert len(classes) == 1
    assert classes[0].name == "UserService"


def test_extract_abstract_class() -> None:
    source = """\
abstract class Repository {
  Future<void> save();
}
"""
    symbols = extract_dart_symbols(source, "repository.dart")
    classes = [s for s in symbols if s.kind == "class"]
    assert len(classes) == 1
    assert classes[0].name == "Repository"


# ── Mixins ───────────────────────────────────────────────────────────────


def test_extract_mixin() -> None:
    source = """\
mixin Loggable {
  void log(String msg) {
    print(msg);
  }
}
"""
    symbols = extract_dart_symbols(source, "loggable.dart")
    mixins = [s for s in symbols if s.kind == "trait"]
    assert len(mixins) == 1
    assert mixins[0].name == "Loggable"


# ── Extensions ───────────────────────────────────────────────────────────


def test_extract_extension() -> None:
    source = """\
extension StringExtension on String {
  String capitalize() {
    return this[0].toUpperCase() + substring(1);
  }
}
"""
    symbols = extract_dart_symbols(source, "string_ext.dart")
    extensions = [s for s in symbols if s.name == "StringExtension"]
    assert len(extensions) == 1
    assert extensions[0].kind == "class"


# ── Enums ────────────────────────────────────────────────────────────────


def test_extract_enum() -> None:
    source = """\
enum Status {
  active,
  inactive,
  pending,
}
"""
    symbols = extract_dart_symbols(source, "status.dart")
    enums = [s for s in symbols if s.kind == "enum"]
    assert len(enums) == 1
    assert enums[0].name == "Status"


# ── Top-level functions ──────────────────────────────────────────────────


def test_extract_top_level_function() -> None:
    source = """\
void main() {
  runApp(MyApp());
}
"""
    symbols = extract_dart_symbols(source, "main.dart")
    functions = [s for s in symbols if s.kind == "function"]
    assert len(functions) == 1
    assert functions[0].name == "main"


# ── Methods ──────────────────────────────────────────────────────────────


def test_extract_methods() -> None:
    source = """\
class Calculator {
  int add(int a, int b) {
    return a + b;
  }

  int subtract(int a, int b) {
    return a - b;
  }
}
"""
    symbols = extract_dart_symbols(source, "calculator.dart")
    methods = [s for s in symbols if s.kind == "method"]
    assert len(methods) == 2
    assert methods[0].parent == "Calculator"


# ── Combined Flutter-like file ───────────────────────────────────────────


def test_extract_flutter_widget_file() -> None:
    """Test extraction from a representative Flutter file."""
    source = """\
import 'package:flutter/material.dart';

enum AppTheme { light, dark }

mixin ThemeMixin {
  ThemeData getTheme(AppTheme theme) {
    return ThemeData();
  }
}

class MyApp extends StatelessWidget {
  const MyApp({super.key});

  Widget build(BuildContext context) {
    return MaterialApp();
  }
}

class HomePage extends StatefulWidget {
  const HomePage({super.key});

  State<HomePage> createState() => _HomePageState();
}

void main() {
  runApp(const MyApp());
}
"""
    symbols = extract_dart_symbols(source, "lib/main.dart")

    names = {s.name for s in symbols}
    assert "AppTheme" in names
    assert "ThemeMixin" in names
    assert "MyApp" in names
    assert "HomePage" in names
    assert "main" in names

    # Check kinds
    kinds = {s.name: s.kind for s in symbols}
    assert kinds["AppTheme"] == "enum"
    assert kinds["ThemeMixin"] == "trait"
    assert kinds["MyApp"] == "class"
    assert kinds["main"] == "function"
