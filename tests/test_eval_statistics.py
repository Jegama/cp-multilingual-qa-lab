"""Tests for mean/deviation aggregation used by the vertical master CSV."""

from parrot_ai.llm_evals.aggregation import aggregate_score_statistics


def _evaluation(
    *,
    biblical: int,
    consistency: int,
    tone: int,
    adherence_overall: int = 4,
) -> dict:
    return {
        "Adherence": {
            "Core": 1,
            "Secondary": 1,
            "Tertiary_Handling": 1,
            "Biblical_Basis": biblical,
            "Consistency": consistency,
            "Overall": adherence_overall,
        },
        "Kindness_and_Gentleness": {
            "Core_Clarity_with_Kindness": 1,
            "Pastoral_Sensitivity": 1,
            "Secondary_Fairness": 1,
            "Tertiary_Neutrality": 1,
            "Tone": tone,
            "Overall": 4,
        },
        "Interfaith_Sensitivity": {
            "Respect_and_Handling_Objections": 1,
            "Objection_Acknowledgement": 1,
            "Evangelism": 1,
            "Gospel_Boldness": 1,
            "Overall": 1,
        },
    }


def _all_false_tag(question: str) -> dict:
    return {
        "question": question,
        "applies_core_doctrine": False,
        "applies_secondary_doctrine": False,
        "applies_tertiary_handling": False,
        "applies_pastoral": False,
        "applies_interfaith": False,
        "applies_evangelism": False,
    }


def test_tagged_statistics_use_the_same_arrays_as_published_means():
    results = [
        {
            "question": "Q1",
            "evaluation": _evaluation(biblical=1, consistency=5, tone=2),
        },
        {
            "question": "Q2",
            "evaluation": _evaluation(biblical=5, consistency=5, tone=4),
        },
    ]
    tags = {question: _all_false_tag(question) for question in ("Q1", "Q2")}

    stats = aggregate_score_statistics(results, False, tags)

    assert stats[("Adherence", "Biblical_Basis")].mean == 3.0
    assert stats[("Adherence", "Biblical_Basis")].stdev == 2.0
    assert stats[("Adherence", "Biblical_Basis")].count == 2

    # Tagged section Overall uses [Biblical_Basis mean=3, Consistency mean=5].
    assert stats[("Adherence", "Overall")].mean == 4.0
    assert stats[("Adherence", "Overall")].stdev == 1.0
    assert stats[("Adherence", "Overall")].count == 2

    # Kindness Overall uses its one applicable component, Tone mean=3.
    assert stats[("Kindness_and_Gentleness", "Overall")].mean == 3.0
    assert stats[("Kindness_and_Gentleness", "Overall")].stdev == 0.0

    # Final uses [Adherence Overall=4, Kindness Overall=3].
    assert stats[("", "Final_Overall")].mean == 3.5
    assert stats[("", "Final_Overall")].stdev == 0.5

    weighted = stats[("", "Weighted_Production_Score")]
    assert weighted.mean == 3.62
    assert weighted.stdev == 0.49
    assert weighted.count == 2


def test_untagged_overall_deviation_uses_raw_per_question_overalls():
    results = [
        {
            "question": "Q1",
            "evaluation": _evaluation(
                biblical=3, consistency=3, tone=3, adherence_overall=1
            ),
        },
        {
            "question": "Q2",
            "evaluation": _evaluation(
                biblical=3, consistency=3, tone=3, adherence_overall=5
            ),
        },
    ]

    stats = aggregate_score_statistics(results, False)

    assert stats[("Adherence", "Overall")].mean == 3.0
    assert stats[("Adherence", "Overall")].stdev == 2.0
    assert stats[("Adherence", "Overall")].count == 2
