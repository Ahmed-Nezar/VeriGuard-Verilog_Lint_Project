# README for Combined Violations Verilog Module

## Overview
The `combined_violations` module is a Verilog code example designed for educational purposes. It demonstrates several common coding mistakes and violations in Verilog design. This module is not intended for practical use in real-world applications but serves as a learning tool for understanding some pitfalls in Verilog coding.

## Violations Demonstrated
The module showcases the following violations:
1. **Arithmetic Overflow**: Occurs when the result of an arithmetic operation exceeds the capacity of the register storing the result.
2. **Unreachable Blocks**: Code blocks that can never be executed due to the logic of the conditional statements.
3. **Unreachable FSM State**: A state in a Finite State Machine (FSM) that cannot be reached due to missing state transitions.
4. **Un-initialized Register**: Demonstrates the undefined behavior that can occur when registers are not initialized.
5. **Multi-Driven Bus/Register**: Occurs when multiple sources drive the same signal, leading to conflicts.
6. **Non Full/Parallel Case**: Highlights issues when not all possible cases are covered in a case statement.
7. **Infer Latch**: Shows how unintentionally a latch can be inferred in the design.
