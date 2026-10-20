"""Check copy counts, title order and root-only wording; no third-party dependencies."""
import json
import re
import sys
import unicodedata
from pathlib import Path


def normalize(value):
    return " ".join(unicodedata.normalize("NFKC", value).casefold().split())


def root_count(text, root):
    text, root = normalize(text), normalize(root)
    if not root:
        raise ValueError("Root must not be blank")
    cjk = bool(re.search(r"[\u3040-\u30ff\u3400-\u9fff]", root))
    pattern = re.escape(root) if cjk else r"(?<!\w)" + re.escape(root) + r"(?!\w)"
    return len(re.findall(pattern, text)), cjk


def required_text(obj, key):
    value = obj.get(key)
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{key} must be non-empty text")
    return value



def uncovered_terms(text, roots):
    """Require full catalog entries; a multiword entry does not license its pieces."""
    text = normalize(text)
    covered = [False] * len(text)
    for root in roots:
        word = normalize(root)
        if not word:
            continue
        pattern = r"(?<!\w)" + re.escape(word) + r"(?!\w)"
        for match in re.finditer(pattern, text):
            covered[match.start():match.end()] = [True] * (match.end() - match.start())
    uncovered = []
    for match in re.finditer(r"\S+", text):
        if any(not covered[i] and not unicodedata.category(text[i]).startswith("P")
               for i in range(match.start(), match.end())):
            uncovered.append(match.group())
    return list(dict.fromkeys(uncovered))


def check_title_sources(title, main, sub, roots, errors, warnings, metrics):
    prefix = title.get("prefix")
    keys = ("brand", "quantity", "total_length", "color")
    if not isinstance(prefix, dict) or any(
            not isinstance(prefix.get(k), str) or not prefix[k].strip() for k in keys):
        errors.append("title.prefix requires brand, quantity, total_length and color")
        tail = main
    else:
        expected = normalize(" ".join(prefix[k] for k in keys))
        actual = normalize(main)
        if not actual.startswith(expected + " "):
            errors.append("title.main must start with brand, quantity, total_length, color in order")
            tail = main
        else:
            tail = actual[len(expected) + 1:]
        metrics["expected_prefix"] = expected
    core = title.get("core_keyword")
    if not isinstance(core, str) or not core.strip():
        errors.append("title.core_keyword is required")
    else:
        canonical = normalize(core)
        if not re.match(re.escape(canonical) + r"(?!\w)", normalize(tail)):
            errors.append("title.core_keyword must immediately follow the fixed prefix")
    if not roots:
        errors.append("A complete source root catalog is required for title source validation")
    else:
        for label, text in (("main_after_prefix", tail), ("subtitle", sub)):
            unknown = uncovered_terms(text, roots)
            metrics[label + "_outside_roots"] = unknown
            if unknown:
                errors.append("Title words outside root catalog (" + label + "): " + ", ".join(unknown))
    if len(main) < 75:
        metrics["remaining_to_75"] = 75 - len(main)
        reason = title.get("capacity_reason")
        warnings.append("Main title is below the 75-character target; review remaining root combinations")
        if not isinstance(reason, str) or not reason.strip():
            errors.append("title.capacity_reason is required when main title is below 75 characters")
        else:
            metrics["capacity_reason"] = reason



def check_bullet_outline(data, bullets, errors, metrics):
    outline = data.get("bullet_outline")
    if not isinstance(outline, list):
        errors.append("bullet_outline is required before generating bullets")
        return
    if len(outline) != 5:
        errors.append(f"Expected 5 outline points; received {len(outline)}")
    seen_topics, seen_claims = {}, {}
    outline_metrics = []
    for index, point in enumerate(outline, 1):
        if not isinstance(point, dict):
            raise ValueError("Each outline point must be an object")
        if type(point.get("point_id")) is not int or point["point_id"] != index:
            errors.append(f"Outline point {index} must have point_id={index}")
        for field in ("topic_id", "focus", "buyer_question"):
            if not isinstance(point.get(field), str) or not point[field].strip():
                errors.append(f"Outline point {index} requires {field}")
        topic = normalize(point.get("topic_id", "")) if isinstance(point.get("topic_id"), str) else ""
        if topic in seen_topics:
            errors.append(f"Repeated bullet topic: {topic} at points {seen_topics[topic]} and {index}")
        elif topic:
            seen_topics[topic] = index
        for field in ("claim_ids", "fact_ids", "root_ids"):
            value = point.get(field)
            if not isinstance(value, list) or not value or any(
                    not isinstance(item, str) or not item.strip() for item in value):
                errors.append(f"Outline point {index} requires non-empty {field}")
        claims = point.get("claim_ids", [])
        if isinstance(claims, list):
            for claim in claims:
                if not isinstance(claim, str):
                    continue
                key = normalize(claim)
                if key in seen_claims:
                    errors.append(f"Repeated primary claim: {claim} at points {seen_claims[key]} and {index}")
                else:
                    seen_claims[key] = index
        if index <= len(bullets):
            bullet = bullets[index - 1]
            if isinstance(bullet, dict):
                for field in ("point_id", "topic_id"):
                    if bullet.get(field) != point.get(field):
                        errors.append(f"Bullet {index} does not match outline {field}")
                if bullet.get("claim_ids") != claims:
                    errors.append(f"Bullet {index} does not match outline claim_ids")
        outline_metrics.append({"point_id": index, "topic_id": topic,
                                "claim_ids": claims})
    metrics["bullet_outline"] = outline_metrics


def check(data):
    if not isinstance(data, dict):
        raise ValueError("Input must be a JSON object")
    errors, warnings, metrics = [], [], {}
    if not any(key in data for key in ("title", "bullets", "qas")):
        raise ValueError("Provide title, bullets, or qas")
    if "title" in data:
        title = data["title"]
        if not isinstance(title, dict):
            raise ValueError("title must be an object")
        main, sub = required_text(title, "main"), required_text(title, "subtitle")
        main_compact = sum(not char.isspace() for char in main)
        metrics["title"] = {"main_without_spaces": main_compact,
                            "main_with_spaces": len(main), "subtitle_with_spaces": len(sub)}
        if len(main) > 75:
            errors.append("title.main exceeds 75 characters including spaces")
        if any(not (char.isalnum() or char == " ") for char in sub):
            errors.append("title.subtitle must contain no punctuation or symbols")
        if not 110 < len(sub) < 125:
            errors.append("title.subtitle must be greater than 110 and less than 125 characters including spaces (111-124)")
        if any(char in main + sub for char in "\r\n\u2028\u2029"):
            errors.append("Title fields must be single-line")
        if any(t != t.strip() or "  " in t or any(c.isspace() and c != " " for c in t)
               for t in (main, sub)):
            errors.append("Title fields require single ordinary spaces and no leading/trailing whitespace")
        for key, text in (("platform_main_limit", main), ("platform_subtitle_limit", sub)):
            limit = title.get(key)
            if limit is None:
                warnings.append(f"{key} not provided; platform length not verified")
            elif type(limit) is not int or limit <= 0:
                raise ValueError(f"{key} must be a positive integer")
            elif len(text) > limit:
                errors.append(f"title exceeds {key}={limit}")
        roots = title.get("roots", [])
        if not isinstance(roots, list) or any(not isinstance(root, str) for root in roots):
            raise ValueError("roots must be a list of strings")
        if any(not normalize(root) for root in roots):
            raise ValueError("Root must not be blank")
        check_title_sources(title, main, sub, roots, errors, warnings, metrics["title"])
        counts, seen = [], set()
        for root in roots:
            normalized = normalize(root)
            if normalized in seen:
                continue
            seen.add(normalized)
            # Match each field separately; do not create a phrase across fields.
            a, cjk = root_count(main, root)
            b, _ = root_count(sub, root)
            counts.append({"root": root, "count": a + b,
                           "match_type": "substring_candidate" if cjk else "literal_boundary"})
            if cjk:
                warnings.append(f"Manually verify continuous-script root: {root}")
            if a + b > 2:
                errors.append(f"Title root occurs more than twice: {root}")
        metrics["title"]["root_counts"] = counts
        warnings.append("Root inflections and platform repeated-word rules require separate review")
    if "bullets" in data:
        bullets = data["bullets"]
        if not isinstance(bullets, list):
            raise ValueError("bullets must be an array")
        if len(bullets) != 5:
            errors.append(f"Expected 5 bullets; received {len(bullets)}")
        check_bullet_outline(data, bullets, errors, metrics)
        metrics["bullets"] = []
        for index, bullet in enumerate(bullets):
            if not isinstance(bullet, dict):
                raise ValueError("Each bullet must be an object")
            text, body = required_text(bullet, "text"), required_text(bullet, "body")
            if not text.endswith(body):
                raise ValueError("Bullet text must end with its complete body")
            target = (150, 150, 400, 400, 400)[index] if index < 5 else None
            punctuation = unicodedata.category(body.rstrip()[-1]).startswith("P")
            metrics["bullets"].append({"index": index + 1, "characters": len(text),
                                      "target": target,
                                      "delta": len(text) - target if target is not None else None,
                                      "terminal_punctuation": punctuation})
            if punctuation:
                errors.append(f"Bullet {index + 1} body ends with punctuation")
        warnings.append("Bullet lengths are soft targets; no user tolerance or platform limits enforced")
    if "qas" in data:
        qas = data["qas"]
        if not isinstance(qas, list):
            raise ValueError("qas must be an array")
        if len(qas) != 10:
            errors.append(f"Expected 10 QAs; received {len(qas)}")
        mode = data.get("qas_delivery_mode")
        if mode not in ("review_candidates", "verified"):
            errors.append("qas_delivery_mode must be review_candidates or verified")
        metrics["qas_delivery_mode"] = mode
        metrics["qas"] = []
        for index, qa in enumerate(qas):
            if not isinstance(qa, dict):
                raise ValueError("Each QA must be an object")
            question, answer = required_text(qa, "question"), required_text(qa, "answer")
            status = qa.get("evidence_status")
            if status not in ("confirmed", "inferred", "unconfirmed"):
                errors.append(f"QA {index + 1} requires a valid evidence_status")
            refs = qa.get("source_refs")
            if not isinstance(refs, list) or not refs:
                errors.append(f"QA {index + 1} requires source_refs")
            if status == "confirmed":
                facts = qa.get("fact_ids")
                if not isinstance(facts, list) or not facts:
                    errors.append(f"QA {index + 1} confirmed answer requires fact_ids")
            elif status in ("inferred", "unconfirmed"):
                note = qa.get("review_note")
                if not isinstance(note, str) or not note.strip():
                    errors.append(f"QA {index + 1} requires review_note for manual review")
                if mode == "verified":
                    errors.append(f"QA {index + 1} is not confirmed for verified mode")
                else:
                    warnings.append(f"QA {index + 1} is a {status} candidate pending user review")
            metrics["qas"].append({"index": index + 1,
                                  "question_characters": len(question),
                                  "answer_characters": len(answer)})
            if len(question) > 100:
                errors.append(f"QA {index + 1} question exceeds 100 characters")
            if len(answer) > 250:
                errors.append(f"QA {index + 1} answer exceeds 250 characters")
    return {"mechanical_passed": not errors, "errors": errors,
            "warnings": warnings, "metrics": metrics,
            "scope": "Counts, title source/order and declared bullet outline consistency only; no factual, semantic, brand, forbidden-term or full platform audit"}


def main():
    if len(sys.argv) != 2:
        print("Usage: python check_copy.py draft.json", file=sys.stderr)
        return 2
    try:
        result = check(json.loads(Path(sys.argv[1]).read_text(encoding="utf-8-sig")))
    except (ValueError, OSError) as error:
        print(json.dumps({"input_error": str(error)}, ensure_ascii=False))
        return 2
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["mechanical_passed"] else 1


if __name__ == "__main__":
    sys.exit(main())
