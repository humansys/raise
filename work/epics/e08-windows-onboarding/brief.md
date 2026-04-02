---
id: E8
title: "Windows Team Onboarding Guide"
status: in-progress
priority: P1
estimated: S (3-4 stories)
---

# E8: Windows Team Onboarding Guide

## Hypothesis

Un equipo nuevo en Windows puede onboardearse a RaiSE sin encontrar los bugs conocidos si documentamos los prerequisites y workarounds de forma explícita antes de que los encuentren.

## Problem

RaiSE tiene bugs activos que afectan exclusivamente a Windows (cp1252 encoding, E4/E7). Sin documentación, el primer `rai graph build` crashea con un traceback críptico. El equipo pierde tiempo debuggeando algo que tiene un workaround de 10 segundos.

## Success Metrics

- Un developer nuevo en Windows puede completar el onboarding sin encontrar ningún bug documentado
- Tiempo de onboarding < 30 minutos desde `pip install` hasta primer `/session-start` exitoso
- Zero tickets de soporte por bugs ya documentados en esta guía

## Appetite

Small — 3-4 stories, scope acotado a documentación y guías. No hay desarrollo de código.

## Rabbit Holes

- Automatizar el fix (modificar el CLI) → fuera de scope, eso es E4/E7
- Guías para Linux/Mac → fuera de scope, solo Windows por ahora
- Video tutorials → fuera de scope, texto es suficiente

## Bet

Vale la pena documentar ahora porque el equipo se onboardea pronto y los bugs no van a estar resueltos a tiempo.
