# Idea 01: intuitive control of power-assisted carts and wheeled platforms

_Status: **real, unfiled idea of the user. CONFIDENTIAL.** Phase 0 working copy. Local only: never paste this text into a search query. Only generated keywords and classification codes go to patent sources. Whether it is already patented or built is unknown._

## Original (as provided, RU)

Идея звучит как интуитивно понятный интерфейс управления тележками и колесными платформами. Примеры: тележки в строительных магазинах, складах, т.е. там где используется большой вес груза и имеются препятствия; медицинская койка с колесами, т.е. там где требуется деликатность и осторожность. Принцип действия: тележка (колесная база) оборудуется двумя управляемыми колесами и двумя неуправляемыми по диагонали, например переднее левое и заднее правое колеса - управляемые, остальные два неуправляемые. Управляемость колеса - это привод по тяге и по повороту на 360 градусов. Модуль управления - удобный эргономичный руль или джойстик или устройство вмонтированное в ручки тележки. Усилие пользователя на ручки тележки интерпретируется в вектор направления тележки с учетом мгновенной скорости/ускорения. Полученный вектор передается на управляющие колеса тележки.

## Technology field

Power-assisted, manually guided wheeled platforms (hand carts, warehouse and retail trolleys, hospital beds, patient transport). The cart is pushed by hand, and a drive amplifies and steers that push. Close neighbours: omnidirectional mobile bases with independently steered drive wheels ("swerve" modules).

## Core idea, split into features

| # | Feature |
|---|---|
| E1 | A four-wheeled base (cart, trolley, wheeled bed) for heavy loads or delicate transport |
| E2 | Exactly **two** of the four wheels are active, each with **traction drive and 360° steering drive** (a steer-and-drive or "swerve" module) |
| E3 | The two active wheels are placed **diagonally** (e.g. front-left and rear-right). The other two wheels are **passive free-swivel casters** |
| E4 | The user interface is an ergonomic handlebar, a joystick, or sensors built into the cart's push handles |
| E5 | The **force the user applies to the handles** is measured and turned into a **desired motion vector** for the cart, taking the instantaneous speed and acceleration into account. The vector is translation only: no commanded rotation |
| E6 | That vector is converted into commands for the active wheels: a steering angle and a traction drive for each of the two wheels |

Application contexts: DIY stores and warehouses (heavy loads, obstacles), hospital beds (smooth, careful motion).

## Clarifications (from the user, 2026-10-01)

- E3: the passive wheels are **free-swivel casters**, so the platform can move in any direction.
- E5: the vector is **translation only** (pushing in a direction). Rotating in place is not part of the idea.

## Candidate classification codes (checked against real hits, 2026-10-01)

| Code | Title | Source |
|---|---|---|
| B62B5/0026 | Hand carts: propulsion aids | probe search + 5 of 7 reference patents |
| B62B5/0069 | … control | 4 of 7 |
| B62B5/0073 | … measuring a force | 4 of 7 |
| B62B5/0033 | … electric motors | 1 of 7 |
| B62B3/001 | Hand carts with more than one axle: steering devices | 4 of 7 |
| B62B2301/00 | Wheel arrangements; steering; stability | 2 of 7 |
| A61G7/08 | Apparatus for transporting beds | probe search + 4 of 7 |
| A61G7/05, A61G7/0528 | Bed parts and details (castors, fifth wheel) | 2 of 7 |
| A61G1/02, A61G1/0275 | Stretchers with wheels | 2 of 7 |
| B60L15/20 | Traction motor speed control | 2 of 7 |

Reference patents used: JP4616127B2 (Toshiba Tec), WO2013054714A1 (KYB), EP2999448B1 (Arjo), US10603234B2 (Stryker), WO2009113009A1 (Borringia), US10406044B2 (Stryker), WO2014159996A1 (Crown).
