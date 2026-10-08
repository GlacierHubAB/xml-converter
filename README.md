# xml-converter

Converts the line-based person format from the old system into the XML
structure the receiving system expects. Written in Python with only the
standard library, no dependencies.

## Usage

Requires Python 3.9 or later.

```
python3 converter.py input.txt      # read from a file
python3 converter.py < input.txt    # or from stdin
```

The XML is written to stdout.

## Tests

```
python3 -m unittest -v
python3 -m doctest converter.py -v
```

## How it works

A T or A line doesn't say who it belongs to; that depends on the lines
before it. The converter therefore keeps two pieces of state while
reading line by line: the current person and the current family member.

- `P` starts a new person and ends any open family member.
- `F` starts a new family member under the current person.
- `T` and `A` go to the current family member if there is one,
  otherwise to the current person.

Which XML each record type produces is defined in the `RECORD_TYPES`
table, so adding a record type is a one-line change.

## Assumptions and design choices

The spec leaves some things open. These are the choices I made:

- **Element order follows the input.** The spec's example shows
  `<address>` before `<phone>` while the input has T before A. If the
  receiving system requires a fixed order, the children can be sorted
  before output.
- **The landline element is named `<landline>`.** The spec only shows
  `<mobile>` followed by `...`.
- **Missing fields are left out.** Obama's address has no postcode, so no
  `<zip>` element is created. Extra fields are currently ignored.
- **Invalid input stops the conversion** with the line number: an unknown
  record type, or T/A/F before any P. Blank lines are skipped. In a real
  integration, skipping the whole broken person and reporting it may be
  preferable; that depends on what the receiving system needs.
- **The whole tree is built in memory.** For very large files, each
  person can be written out as soon as the next P arrives.
