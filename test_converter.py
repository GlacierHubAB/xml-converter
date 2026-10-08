import unittest

from converter import convert, parse_line, to_xml_string


class ParseLineTest(unittest.TestCase):
    def test_splits_code_and_values(self):
        self.assertEqual(parse_line("P|Carl Gustaf|Bernadotte\n"), ("P", ["Carl Gustaf", "Bernadotte"]))

    def test_strips_whitespace_around_fields(self):
        self.assertEqual(parse_line(" T | 070 | 08 "), ("T", ["070", "08"]))


class ConvertTest(unittest.TestCase):
    def test_person_gets_names(self):
        person = convert(["P|Barack|Obama"]).find("person")
        self.assertEqual(person.findtext("firstname"), "Barack")
        self.assertEqual(person.findtext("lastname"), "Obama")

    def test_phone_and_address_after_person_belong_to_person(self):
        person = convert(["P|A|B", "T|070|08", "A|Gatan 1|Stad|123"]).find("person")
        self.assertEqual(person.findtext("phone/mobile"), "070")
        self.assertEqual(person.findtext("address/zip"), "123")

    def test_records_after_family_belong_to_family(self):
        person = convert(["P|A|B", "F|Victoria|1977", "A|Haga|Stockholm|10002"]).find("person")
        self.assertIsNone(person.find("address"))
        self.assertEqual(person.findtext("family/address/street"), "Haga")

    def test_new_family_closes_previous_family(self):
        person = convert(["P|A|B", "F|X|1", "F|Y|2", "T|070|08"]).find("person")
        first, second = person.findall("family")
        self.assertIsNone(first.find("phone"))
        self.assertEqual(second.findtext("phone/mobile"), "070")

    def test_new_person_closes_family(self):
        root = convert(["P|A|B", "F|X|1", "P|C|D", "A|Gatan|Stad"])
        second = root.findall("person")[1]
        self.assertEqual(second.findtext("address/street"), "Gatan")

    def test_missing_fields_are_omitted(self):
        address = convert(["P|A|B", "A|Gatan|Stad"]).find("person/address")
        self.assertIsNone(address.find("zip"))

    def test_blank_lines_are_ignored(self):
        self.assertEqual(len(convert(["P|A|B", "", "  ", "P|C|D"])), 2)

    def test_special_characters_are_escaped(self):
        xml = to_xml_string(convert(["P|Tom & Jerry|<Ö>"]))
        self.assertIn("Tom &amp; Jerry", xml)
        self.assertIn("&lt;Ö&gt;", xml)

    def test_unknown_record_type_raises(self):
        with self.assertRaisesRegex(ValueError, "Line 2"):
            convert(["P|A|B", "X|oops"])

    def test_record_before_person_raises(self):
        with self.assertRaisesRegex(ValueError, "Line 1"):
            convert(["T|070|08"])


if __name__ == "__main__":
    unittest.main()
