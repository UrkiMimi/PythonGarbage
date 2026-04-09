#!/usr/bin/env python3
"""
Assembler for Umazing Instruction Set
====================================
Supports .asm files and is designed for easy addition of future instructions.

Usage:
    python uasm.py input.asm output.bin
    python uasm.py input.asm              # outputs input.bin

Instruction Set Format:
    Each instruction is defined in INSTRUCTION_SET below.
    To add a new instruction, simply add an entry to that dict.

.asm File Syntax:
    ; comment
    label:          ; define a label (used as jump target)
    MNEMONIC        ; zero-operand instruction
    MNEMONIC value  ; one-operand instruction (decimal or 0x hex)
    MNEMONIC label  ; one-operand instruction referencing a label
"""

import sys
import re
from dataclasses import dataclass, field
from typing import Optional, Callable


# ─────────────────────────────────────────────────────────────────────────────
# Instruction Definition
# ─────────────────────────────────────────────────────────────────────────────

@dataclass
class InstructionDef:
    """Describes a single instruction in the ISA."""
    mnemonic: str          # Assembly keyword, e.g. "add"
    opcode: int            # Machine opcode byte, e.g. 0x80
    operands: int          # Number of operand bytes following the opcode (0 or 1)
    description: str = ""  # Human-readable description
    # Optional custom encoder: receives (operand_value) -> list[int]
    # If None, default encoding is used (little-endian byte stream)
    encoder: Optional[Callable[[Optional[int]], list[int]]] = field(
        default=None, repr=False
    )

    def encode(self, operands: list[int]) -> list[int]:
        """Return the byte sequence for this instruction."""
        if self.encoder:
            return self.encoder(operands)
        # Default: opcode byte followed by operand bytes (little-endian, one byte each)
        result = [self.opcode]
        for operand in operands:
            result.append(operand & 0xFF)
        return result


# ─────────────────────────────────────────────────────────────────────────────
# Instruction Set Table
# ─────────────────────────────────────────────────────────────────────────────
# To add a new instruction:
#   1. Pick a mnemonic and an opcode.
#   2. Add an InstructionDef entry here.
#   3. That's it — the assembler picks it up automatically.

INSTRUCTION_SET: dict[str, InstructionDef] = {
    instr.mnemonic: instr
    for instr in [
        InstructionDef(
            mnemonic="adda",
            opcode=0x80,
            operands=0,
            description="Increment regA by 1 (mod 255)",
        ),
        InstructionDef(
            mnemonic="suba",
            opcode=0x81,
            operands=0,
            description="Decrement regA by 1 (mod 255)",
        ),
        InstructionDef(
            mnemonic="awta",
            opcode=0x82,
            operands=1,
            description="Write register A to RAM, advance pc",
        ),
        InstructionDef(
            mnemonic="rdaa",
            opcode=0x83,
            operands=1,
            description="Read byte from ROM, advance pc",
        ),
        InstructionDef(
            mnemonic="seta",
            opcode=0x87,
            operands=1,
            description="Set regA to immediate value (1-byte operand)",
        ),
        InstructionDef(
            mnemonic="bea",
            opcode=0x8A,
            operands=2,
            description="Branch jump for register A",
        ),
        InstructionDef(
            mnemonic="hlt",
            opcode=0x84,
            operands=0,
            description="Halt the ALU",
        ),
        InstructionDef(
            mnemonic="upd",
            opcode=0x85,
            operands=0,
            description="Update / flush the screen buffer",
        ),
        InstructionDef(
            mnemonic="jmp",
            opcode=0x88,
            operands=1,
            description="Jump: set pc to address (1-byte operand or label)",
        ),
        InstructionDef(
            mnemonic="addx",
            opcode=0xA0,
            operands=0,
            description="Increments one to register X",
        ),
        InstructionDef(
            mnemonic="subx",
            opcode=0xA1,
            operands=0,
            description="Decrements one to register X",
        ),
        InstructionDef(
            mnemonic="awtx",
            opcode=0xA2,
            operands=1,
            description="Write register X to RAM",
        ),
        InstructionDef(
            mnemonic="rdax",
            opcode=0xA3,
            operands=1,
            description="Sets register X to operand",
        ),
        InstructionDef(
            mnemonic="setx",
            opcode=0xA7,
            operands=1,
            description="Explicitly sets register X to operand",
        ),
        InstructionDef(
            mnemonic="awxx",
            opcode=0xAA,
            operands=0,
            description="Write register X to RAM using address from register A",
        ),
        InstructionDef(
            mnemonic="rdxx",
            opcode=0xAB,
            operands=0,
            description="Unimplemented",
        ),
        # ── Add future instructions below this line ──────────────────────────
        # Example:
        # InstructionDef(
        #     mnemonic="nop",
        #     opcode=0x86,
        #     operands=0,
        #     description="No operation",
        # ),
    ]
}


# ─────────────────────────────────────────────────────────────────────────────
# Errors
# ─────────────────────────────────────────────────────────────────────────────

class AssemblerError(Exception):
    """Raised for any assembly-time error."""
    def __init__(self, message: str, line_no: int = -1, line: str = ""):
        loc = f"line {line_no}: " if line_no >= 0 else ""
        src = f"  → {line.strip()}" if line else ""
        super().__init__(f"{loc}{message}{src}")


# ─────────────────────────────────────────────────────────────────────────────
# Tokeniser / Parser
# ─────────────────────────────────────────────────────────────────────────────

COMMENT_RE   = re.compile(r";.*$")
LABEL_RE     = re.compile(r"^([A-Za-z_]\w*):$")
NUMBER_RE    = re.compile(r"^(0x[0-9A-Fa-f]+|\d+)$")
LABEL_REF_RE = re.compile(r"^[A-Za-z_]\w*$")


def parse_number(token: str) -> int:
    if token.startswith("0x") or token.startswith("0X"):
        return int(token, 16)
    return int(token, 10)


@dataclass
class Statement:
    """One logical line of assembly after parsing."""
    line_no: int
    label: Optional[str]        # label defined on this line (may be None)
    mnemonic: Optional[str]     # instruction mnemonic (may be None for label-only lines)
    operand_tokens: list[str]   # raw operand strings (empty list if none)


def tokenise(source: str) -> list[Statement]:
    """Split source text into Statement objects."""
    statements: list[Statement] = []

    for line_no, raw_line in enumerate(source.splitlines(), start=1):
        line = COMMENT_RE.sub("", raw_line).strip()
        if not line:
            continue

        label = None
        mnemonic = None

        # Check for label definition (possibly alone on the line)
        label_match = LABEL_RE.match(line)
        if label_match:
            label = label_match.group(1).lower()
            statements.append(Statement(line_no, label, None, []))
            continue

        # Check for inline label prefix: "start: set 0x10"
        inline_label_match = re.match(r"^([A-Za-z_]\w*):\s+(.+)$", line)
        if inline_label_match:
            label = inline_label_match.group(1).lower()
            line = inline_label_match.group(2).strip()

        tokens = line.split()
        mnemonic = tokens[0].lower()
        operand_tokens = tokens[1:]  # everything after the mnemonic

        statements.append(Statement(line_no, label, mnemonic, operand_tokens))

    return statements


# ─────────────────────────────────────────────────────────────────────────────
# Two-Pass Assembler
# ─────────────────────────────────────────────────────────────────────────────

def assemble(source: str, origin: int = 0x00) -> bytes:
    """
    Assemble source text into a binary blob.

    Parameters
    ----------
    source : str
        Full text of the .asm file.
    origin : int
        Starting address of the output (default 0x00).
        Used for label resolution.

    Returns
    -------
    bytes
        Raw machine code.
    """
    statements = tokenise(source)

    # ── Pass 1: collect labels ────────────────────────────────────────────────
    labels: dict[str, int] = {}
    pc = origin

    for stmt in statements:
        if stmt.label:
            if stmt.label in labels:
                raise AssemblerError(
                    f"Duplicate label '{stmt.label}'",
                    stmt.line_no,
                )
            labels[stmt.label] = pc

        if stmt.mnemonic:
            if stmt.mnemonic not in INSTRUCTION_SET:
                raise AssemblerError(
                    f"Unknown mnemonic '{stmt.mnemonic}'",
                    stmt.line_no,
                )
            instr_def = INSTRUCTION_SET[stmt.mnemonic]
            # Each instruction emits (1 opcode + operand bytes) bytes
            pc += 1 + instr_def.operands

    # ── Pass 2: emit bytes ────────────────────────────────────────────────────
    output: list[int] = []

    for stmt in statements:
        if not stmt.mnemonic:
            continue  # label-only line

        instr_def = INSTRUCTION_SET[stmt.mnemonic]

        # Resolve operands
        resolved: list[int] = []
        if len(stmt.operand_tokens) != instr_def.operands:
            raise AssemblerError(
                f"'{stmt.mnemonic}' expects {instr_def.operands} operand(s), "
                f"got {len(stmt.operand_tokens)}",
                stmt.line_no,
            )
        for tok in stmt.operand_tokens:
            if NUMBER_RE.match(tok):
                resolved.append(parse_number(tok))
            elif LABEL_REF_RE.match(tok):
                label_key = tok.lower()
                if label_key not in labels:
                    raise AssemblerError(
                        f"Undefined label '{tok}'",
                        stmt.line_no,
                    )
                resolved.append(labels[label_key])
            else:
                raise AssemblerError(
                    f"Invalid operand '{tok}'",
                    stmt.line_no,
                )

        output.extend(instr_def.encode(resolved))

    return bytes(output)


# ─────────────────────────────────────────────────────────────────────────────
# CLI
# ─────────────────────────────────────────────────────────────────────────────

def _list_instructions() -> None:
    print(f"{'Mnemonic':<10} {'Opcode':<8} {'Operands':<10} Description")
    print("─" * 60)
    for name, instr in sorted(INSTRUCTION_SET.items(), key=lambda x: x[1].opcode):
        print(
            f"{instr.mnemonic:<10} "
            f"0x{instr.opcode:02X}    "
            f"{instr.operands:<10} "
            f"{instr.description}"
        )


def main(argv: list[str]) -> int:
    import argparse, pathlib

    parser = argparse.ArgumentParser(
        description="Extensible assembler for custom ISA.",
        epilog="Example: python assembler.py program.asm program.bin",
    )
    parser.add_argument("input",  nargs="?", help=".asm source file")
    parser.add_argument("output", nargs="?", help="output binary (default: <input>.bin)")
    parser.add_argument(
        "--origin", "-o", type=lambda s: int(s, 0), default=0,
        help="starting address for label resolution (default: 0x00)",
    )
    parser.add_argument(
        "--list-instructions", "-l", action="store_true",
        help="print the instruction set and exit",
    )
    parser.add_argument(
        "--hex", "-x", action="store_true",
        help="also print a hex dump of the output",
    )

    args = parser.parse_args(argv)

    if args.list_instructions:
        _list_instructions()
        return 0

    if not args.input:
        parser.print_help()
        return 1

    src_path = pathlib.Path(args.input)
    if not src_path.exists():
        print(f"Error: file not found: {src_path}", file=sys.stderr)
        return 1

    out_path = pathlib.Path(args.output) if args.output else src_path.with_suffix(".bin")

    try:
        source = src_path.read_text(encoding="utf-8")
        binary = assemble(source, origin=args.origin)
    except AssemblerError as exc:
        print(f"Assembly error: {exc}", file=sys.stderr)
        return 1

    out_path.write_bytes(binary)
    print(f"Assembled {len(binary)} byte(s) → {out_path}")

    if args.hex:
        print("\nHex dump:")
        for i in range(0, len(binary), 16):
            chunk = binary[i:i+16]
            hex_part  = " ".join(f"{b:02X}" for b in chunk)
            ascii_part = "".join(chr(b) if 32 <= b < 127 else "." for b in chunk)
            print(f"  {i+args.origin:04X}  {hex_part:<48}  {ascii_part}")

    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))