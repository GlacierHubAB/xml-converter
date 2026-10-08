import sys
import xml.etree.ElementTree as ET

# Record code -> (XML tag, names of the child elements, in field order)
RECORD_TYPES = {
    "P": ("person", ["firstname", "lastname"]),
    "T": ("phone", ["mobile", "landline"]),
    "A": ("address", ["street", "city", "zip"]),
    "F": ("family", ["name", "born"]),
}


def parse_line(line):
    """Split a record line into its code and field values.

    >>> parse_line("T|0768-101801|08-101801\\n")
    ('T', ['0768-101801', '08-101801'])
    """
    parts = [part.strip() for part in line.strip().split("|")]
    return parts[0], parts[1:]


def add_record(parent, code, values):
    """Append the record as a child element of parent and return it.

    add_record(person, "A", ["Haga Slott", "Stockholm", "10002"]) adds:
        <address>
          <street>Haga Slott</street>
          <city>Stockholm</city>
          <zip>10002</zip>
        </address>

    Missing values are left out; extra values are ignored.
    """
    tag, field_names = RECORD_TYPES[code]
    element = ET.SubElement(parent, tag)
    for name, value in zip(field_names, values):
        ET.SubElement(element, name).text = value
    return element


def convert(lines):
    """Turn the line-based format into a <people> XML tree.

    T and A records belong to the most recent F if there is one,
    otherwise to the most recent P. A new P ends the current family member.
    """
    root = ET.Element("people")
    current_person = None
    current_family = None

    for line_number, line in enumerate(lines, start=1):
        if not line.strip():
            continue

        code, values = parse_line(line)

        if code not in RECORD_TYPES:
            raise ValueError(f"Line {line_number}: unknown record type {code!r}")

        if code == "P":
            current_person = add_record(root, code, values)
            current_family = None
            continue

        if current_person is None:
            raise ValueError(f"Line {line_number}: {code!r} record before any person")

        if code == "F":
            current_family = add_record(current_person, code, values)
        else:
            owner = current_family if current_family is not None else current_person
            add_record(owner, code, values)

    return root


def to_xml_string(root):
    ET.indent(root)
    return ET.tostring(root, encoding="unicode")


def main():
    if len(sys.argv) > 1:
        with open(sys.argv[1], encoding="utf-8") as f:
            root = convert(f)
    else:
        root = convert(sys.stdin)

    print(to_xml_string(root))


if __name__ == "__main__":
    main()
