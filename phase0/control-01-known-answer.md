# Control 01: known-answer recall test (not confidential)

**Hidden answer:** JP4616127B2 (Toshiba Tec, "Power assist vehicle", priority 2005-08-25, family 37919331).
Step 7 passes if this patent or any member of its family ranks in the top 20.
Don't give the pipeline the answer or the assignee name. Only the "idea" text below is its input.

## Idea text (rewritten from claim 1 in plain language, with no claim wording)

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
