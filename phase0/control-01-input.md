# Control 01: input for a blind recall test

This is a test idea, not confidential. It's the only input the pipeline gets.

## Idea text

A hand-pushed cart, such as a shopping or warehouse trolley, gets an electric drive that helps the person pushing it.
Sensors in the push handle measure how hard the person is pushing and in which direction.
The cart also carries obstacle sensors that detect objects in its path and measure how far away they are and in which direction.
From each detected obstacle, the controller computes a virtual "repulsive" force that pushes the cart away from it, stronger the closer the obstacle is.
It adds this virtual force to the person's measured push and uses the combined force to decide how much drive assistance to give and in which direction.
The cart therefore feels light to push, but gently steers itself away from walls, shelves and people without the operator having to react.

## Features (for scoring the comparison step)

| # | Feature |
|---|---|
| C1 | A hand-pushed cart with an electric drive that assists the push |
| C2 | Handle sensors measure the magnitude and direction of the operator's force |
| C3 | Obstacle sensors measure distance and direction to obstacles |
| C4 | A virtual repulsive force is computed from each obstacle's distance and direction |
| C5 | The assist force is computed from the operator force plus the repulsive force, and the drive is controlled from it |
