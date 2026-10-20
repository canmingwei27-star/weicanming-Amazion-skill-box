"""Behavioral regression checks for title order, length and source restrictions."""
import copy
import unittest
from check_copy import check, uncovered_terms


class TitleChecks(unittest.TestCase):
    def fixture(self):
        return {"title": {
            "main": "Bijou Joon 4 Rolls 88 Feet Purple Pearl String Garland Beads Faux DIY Craft",
            "subtitle": "Pearl Strands Crafting Wedding Bouquet Table Decor Christmas Tree Decorations Round ABS Plastic Beads Artificial Trim",
            "prefix": {"brand": "Bijou Joon", "quantity": "4 Rolls",
                       "total_length": "88 Feet", "color": "Purple"},
            "core_keyword": "Pearl String",
            "roots": ["pearl", "string", "garland", "beads", "faux", "diy", "craft",
                      "strands", "wedding", "christmas", "tree", "crafting", "bouquet",
                      "table", "decor", "decorations", "round", "abs", "plastic", "artificial", "trim"],
            "platform_main_limit": 75, "platform_subtitle_limit": 125}}

    def errors(self, data):
        return check(data)["errors"]

    def test_valid_75_and_fact_prefix_exception(self):
        data = self.fixture()
        self.assertEqual(len(data["title"]["main"]), 75)
        self.assertTrue(check(data)["mechanical_passed"])
        self.assertNotIn("purple", data["title"]["roots"])

    def test_76_is_rejected(self):
        data = self.fixture()
        data["title"]["main"] = data["title"]["main"].replace("Craft", "Crafts")
        data["title"]["roots"].append("crafts")
        self.assertTrue(any("exceeds 75" in e for e in self.errors(data)))

    def test_removed_65_nonspace_cap(self):
        data = self.fixture()
        prefix = {"brand": "B", "quantity": "4 Rolls", "total_length": "88 Feet", "color": "Purple"}
        start = " ".join(prefix.values())
        core = "p" * (75 - len(start) - 1)
        data["title"].update(prefix=prefix, main=start + " " + core, core_keyword=core,
                             roots=data["title"]["roots"] + [core])
        self.assertGreater(len(data["title"]["main"].replace(" ", "")), 65)
        self.assertTrue(check(data)["mechanical_passed"])

    def test_brand_and_quantity_order_enforced(self):
        data = self.fixture()
        data["title"]["main"] = data["title"]["main"].replace("Bijou Joon 4 Rolls", "4 Rolls Bijou Joon")
        self.assertTrue(any("must start" in e for e in self.errors(data)))

    def test_core_must_follow_color(self):
        data = self.fixture()
        data["title"]["core_keyword"] = "Garland"
        self.assertTrue(any("immediately follow" in e for e in self.errors(data)))

    def test_unknown_main_word_rejected(self):
        data = self.fixture()
        data["title"]["main"] = data["title"]["main"].replace("Faux", "Full")
        self.assertTrue(any("outside root catalog (main_after_prefix)" in e for e in self.errors(data)))

    def test_subtitle_has_no_fact_or_grammar_exemption(self):
        for text in ("Purple", "Full Round", "Cut to Length", "Wedding for Crafts"):
            with self.subTest(text=text):
                data = self.fixture()
                data["title"]["subtitle"] = text
                self.assertTrue(any("outside root catalog (subtitle)" in e for e in self.errors(data)))

    def test_missing_sources_cannot_pass(self):
        data = self.fixture()
        data["title"]["roots"] = []
        self.assertFalse(check(data)["mechanical_passed"])
        data = self.fixture()
        del data["title"]["prefix"]
        self.assertFalse(check(data)["mechanical_passed"])

    def test_cannot_split_multiword_root(self):
        self.assertEqual(uncovered_terms("silk", ["silk ribbon"]), ["silk"])
        self.assertEqual(uncovered_terms("Silk Ribbon", ["silk ribbon"]), [])

    def test_repetition_still_checked(self):
        data = self.fixture()
        data["title"]["subtitle"] = "Pearl Pearl"
        self.assertTrue(any("more than twice" in e for e in self.errors(data)))

    def test_no_padding_to_reach_target(self):
        data = self.fixture()
        data["title"]["main"] = data["title"]["main"].replace("Faux ", "Faux  ")
        self.assertTrue(any("single ordinary spaces" in e for e in self.errors(data)))

    def test_short_title_requires_reason(self):
        data = self.fixture()
        data["title"]["main"] = data["title"]["main"].removesuffix(" Craft")
        self.assertTrue(any("capacity_reason" in e for e in self.errors(data)))
        data["title"]["capacity_reason"] = "Example limitation for this fixture"
        self.assertTrue(check(data)["mechanical_passed"])
        self.assertTrue(check(data)["warnings"])

    def test_subtitle_strict_boundaries(self):
        for size in (33, 109, 110, 111, 112, 123, 124, 125, 126):
            with self.subTest(size=size):
                data = self.fixture()
                data["title"]["subtitle"] = "x" * size
                data["title"]["roots"].append("x" * size)
                self.assertEqual(check(data)["mechanical_passed"], 111 <= size <= 124)

    def test_subtitle_limit_counts_spaces(self):
        data = self.fixture()
        subtitle = data["title"]["subtitle"]
        self.assertLessEqual(len(subtitle.replace(" ", "")), 110)
        self.assertGreater(len(subtitle), 110)
        self.assertTrue(check(data)["mechanical_passed"])

    def test_platform_limit_remains_independent(self):
        data = self.fixture()
        data["title"]["platform_subtitle_limit"] = 110
        self.assertTrue(any("platform_subtitle_limit=110" in e for e in self.errors(data)))

    def test_bullets_without_outline_rejected(self):
        data = {"bullets": [{"text": "Label: Actual text", "body": "Actual text"} for _ in range(5)]}
        self.assertFalse(check(data)["mechanical_passed"])



class BulletOutlineChecks(unittest.TestCase):
    def fixture(self):
        topics = ["specifications", "cut_retention", "wedding_use", "christmas_use", "diy_tying"]
        outline = [{"point_id": i, "topic_id": t, "focus": t,
                    "buyer_question": "What does this point explain?",
                    "claim_ids": [t], "fact_ids": ["shared_source_fact"],
                    "root_ids": ["source_root"]} for i, t in enumerate(topics, 1)]
        bullets = [{"point_id": p["point_id"], "topic_id": p["topic_id"],
                    "claim_ids": p["claim_ids"].copy(), "text": "Label: Actual text",
                    "body": "Actual text"} for p in outline]
        return {"bullet_outline": outline, "bullets": bullets}

    def test_distinct_plan_and_shared_support_fact_pass(self):
        self.assertTrue(check(self.fixture())["mechanical_passed"])

    def test_two_size_points_rejected(self):
        data = self.fixture()
        data["bullet_outline"][3]["topic_id"] = "specifications"
        data["bullets"][3]["topic_id"] = "specifications"
        self.assertTrue(any("Repeated bullet topic" in e for e in check(data)["errors"]))

    def test_renamed_topic_cannot_repeat_primary_claim(self):
        data = self.fixture()
        data["bullet_outline"][3]["claim_ids"] = ["specifications"]
        data["bullets"][3]["claim_ids"] = ["specifications"]
        self.assertTrue(any("Repeated primary claim" in e for e in check(data)["errors"]))

    def test_draft_must_follow_plan(self):
        data = self.fixture()
        data["bullets"][3]["topic_id"] = "new_topic"
        self.assertTrue(any("does not match" in e for e in check(data)["errors"]))

    def test_missing_roots_or_facts_is_exposed(self):
        for key in ("root_ids", "fact_ids"):
            with self.subTest(key=key):
                data = self.fixture()
                data["bullet_outline"][2][key] = []
                self.assertFalse(check(data)["mechanical_passed"])

    def test_outline_order_enforced(self):
        data = self.fixture()
        data["bullet_outline"][1]["point_id"] = 4
        self.assertFalse(check(data)["mechanical_passed"])

    def test_partial_plan_is_not_complete(self):
        data = self.fixture()
        data["bullet_outline"].pop()
        data["bullets"].pop()
        self.assertFalse(check(data)["mechanical_passed"])

    def test_claim_drift_rejected(self):
        data = self.fixture()
        data["bullets"][3]["claim_ids"] = ["unplanned_claim"]
        self.assertTrue(any("claim_ids" in e for e in check(data)["errors"]))



class ReviewCandidateChecks(unittest.TestCase):
    def fixture(self):
        return {"qas_delivery_mode": "review_candidates", "qas": [
            {"question": f"Can I use this for project {i}?", "answer": "Try arranging it as a decorative accent before securing it.",
             "evidence_status": "unconfirmed", "review_note": "Check suitability for this use", "source_refs": ["keyword_source"], "fact_ids": []}
            for i in range(10)]}

    def test_ten_unconfirmed_candidates_can_be_delivered(self):
        result = check(self.fixture())
        self.assertTrue(result["mechanical_passed"])
        self.assertTrue(result["warnings"])

    def test_verified_rejects_unconfirmed_answers(self):
        d=self.fixture();d["qas_delivery_mode"]="verified"
        self.assertFalse(check(d)["mechanical_passed"])

    def test_unlabeled_assumption_cannot_pass(self):
        d=self.fixture();d["qas"][0]["review_note"]=""
        self.assertFalse(check(d)["mechanical_passed"])

    def test_confirmed_requires_evidence(self):
        d=self.fixture();d["qas"][0]["evidence_status"]="confirmed"
        self.assertFalse(check(d)["mechanical_passed"])
        d["qas"][0]["fact_ids"]=["F01"]
        self.assertTrue(check(d)["mechanical_passed"])

    def test_nine_candidates_not_complete(self):
        d=self.fixture();d["qas"].pop()
        self.assertFalse(check(d)["mechanical_passed"])

    def test_qa_source_and_length_still_required(self):
        d=self.fixture();d["qas"][0]["source_refs"]=[]
        self.assertFalse(check(d)["mechanical_passed"])
        d=self.fixture();d["qas"][0]["answer"]="x"*251
        self.assertFalse(check(d)["mechanical_passed"])

    def test_subtitle_punctuation_and_symbols_rejected(self):
        for mark in [",", ".", ":", "-", "/", "&", "（", "✨"]:
            d=TitleChecks().fixture();d["title"]["subtitle"]="Wedding"+mark+" Christmas Tree"
            self.assertTrue(any("no punctuation" in e for e in check(d)["errors"]))

    def test_plain_subtitle_still_passes(self):
        self.assertTrue(check(TitleChecks().fixture())["mechanical_passed"])

if __name__ == "__main__":
    unittest.main()
