from __future__ import annotations

import pandas as pd
import pytest

import splink.comparison_library as cl
from splink import SettingsCreator, block_on
from splink.internals.realtime import compare_records

from .decorator import mark_with_dialects_excluding

dummies = []


@mark_with_dialects_excluding()
def test_realtime_cache_two_records(test_helpers, dialect):
    # Test that you get the same result whether you cache the SQL
    # or not with different records

    helper = test_helpers[dialect]

    db_api = helper.extra_linker_args()["db_api"]

    df1 = pd.DataFrame(
        [
            {
                "unique_id": 0,
                "first_name": "Julia ",
                "surname": "Taylor",
                "city": "London",
                "email": "hannah88@powers.com",
                "tf_city": 0.2,
                "tf_first_name": 0.1,
            }
        ]
    )

    df2 = pd.DataFrame(
        [
            {
                "unique_id": 2,
                "first_name": "Julia ",
                "surname": "Taylor",
                "city": "London",
                "email": "hannah88@powers.com",
                "cluster": 0,
                "tf_city": 0.2,
                "tf_first_name": 0.1,
            },
        ]
    )

    df3 = pd.DataFrame(
        [
            {
                "unique_id": 4,
                "first_name": "Noah",
                "surname": "Watson",
                "city": "Bolton",
                "email": "matthew78@ballard-mcdonald.net",
                "cluster": 1,
                "tf_city": 0.01,
                "tf_first_name": 0.01,
            },
        ]
    )

    settings = SettingsCreator(
        link_type="dedupe_only",
        comparisons=[
            cl.ExactMatch("first_name").configure(term_frequency_adjustments=True),
            cl.ExactMatch("surname"),
            cl.ExactMatch("city").configure(term_frequency_adjustments=True),
            cl.ExactMatch("email"),
        ],
        blocking_rules_to_generate_predictions=[
            block_on("first_name"),
            block_on("surname"),
        ],
        max_iterations=2,
        retain_intermediate_calculation_columns=True,
        retain_matching_columns=True,
    )

    res1_2_first, dummy = compare_records(df1, df2, settings, db_api)
    dummies.append(dummy)
    res1_2_first = res1_2_first.as_record_dict()[0]["match_weight"]

    res1_2_not_from_cache, dummy = compare_records(
        df1, df2, settings, db_api, use_sql_from_cache=False
    )
    dummies.append(dummy)
    res1_2_not_from_cache = res1_2_not_from_cache.as_record_dict()[0]["match_weight"]

    res1_2_from_cache, dummy = compare_records(
        df1, df2, settings, db_api, use_sql_from_cache=True
    )
    dummies.append(dummy)
    res1_2_from_cache = res1_2_from_cache.as_record_dict()[0]["match_weight"]

    assert res1_2_first == pytest.approx(res1_2_not_from_cache)
    assert res1_2_first == pytest.approx(res1_2_from_cache)

    res1_3_first, dummy = compare_records(df1, df3, settings, db_api)
    dummies.append(dummy)
    res1_3_first = res1_3_first.as_record_dict()[0]["match_weight"]
    res1_3_not_from_cache, dummy = compare_records(
        df1, df3, settings, db_api, use_sql_from_cache=False
    )
    dummies.append(dummy)
    res1_3_not_from_cache = res1_3_not_from_cache.as_record_dict()[0]["match_weight"]
    res1_3_from_cache, dummy = compare_records(
        df1, df3, settings, db_api, use_sql_from_cache=True
    )
    dummies.append(dummy)
    res1_3_from_cache = res1_3_from_cache.as_record_dict()[0]["match_weight"]

    assert res1_3_first == pytest.approx(res1_3_not_from_cache)
    assert res1_3_first == pytest.approx(res1_3_from_cache)

    assert res1_2_first != pytest.approx(res1_3_first)


@mark_with_dialects_excluding()
def test_realtime_cache_multiple_records(test_helpers, dialect):
    # Test that you get the same result whether you cache the SQL
    # or not with multiple records in each DataFrame

    helper = test_helpers[dialect]
    db_api = helper.extra_linker_args()["db_api"]

    df1 = pd.DataFrame(
        [
            {
                "unique_id": 0,
                "first_name": "Julia",
                "surname": "Taylor",
                "city": "London",
                "email": "hannah88@powers.com",
                "tf_city": 0.2,
                "tf_first_name": 0.1,
            },
            {
                "unique_id": 1,
                "first_name": "John",
                "surname": "Smith",
                "city": "Manchester",
                "email": "john.smith@email.com",
                "tf_city": 0.2,
                "tf_first_name": 0.1,
            },
        ]
    )

    df2 = pd.DataFrame(
        [
            {
                "unique_id": 2,
                "first_name": "Julia",
                "surname": "Taylor",
                "city": "London",
                "email": "hannah88@powers.com",
                "cluster": 0,
                "tf_city": 0.2,
                "tf_first_name": 0.1,
            },
            {
                "unique_id": 3,
                "first_name": "Jane",
                "surname": "Wilson",
                "city": "Birmingham",
                "email": "jane.w@example.com",
                "cluster": 1,
                "tf_city": 0.2,
                "tf_first_name": 0.1,
            },
        ]
    )

    df3 = pd.DataFrame(
        [
            {
                "unique_id": 4,
                "first_name": "Noah",
                "surname": "Watson",
                "city": "Bolton",
                "email": "matthew78@ballard-mcdonald.net",
                "cluster": 2,
                "tf_city": 0.2,
                "tf_first_name": 0.1,
            },
            {
                "unique_id": 5,
                "first_name": "Emma",
                "surname": "Brown",
                "city": "Leeds",
                "email": "emma.b@test.com",
                "cluster": 3,
                "tf_city": 0.2,
                "tf_first_name": 0.1,
            },
            {
                "unique_id": 6,
                "first_name": "Oliver",
                "surname": "Davies",
                "city": "Bristol",
                "email": "oliver.d@example.net",
                "cluster": 4,
                "tf_city": 0.2,
                "tf_first_name": 0.1,
            },
        ]
    )

    # Add required columns if they don't exist
    for frame in [df1, df2, df3]:
        if "tf_city" not in frame.columns:
            frame["tf_city"] = 0.2
        if "tf_first_name" not in frame.columns:
            frame["tf_first_name"] = 0.1
        if "cluster" not in frame.columns and frame is not df1:
            frame["cluster"] = range(len(frame))

    settings = SettingsCreator(
        link_type="dedupe_only",
        comparisons=[
            cl.ExactMatch("first_name").configure(term_frequency_adjustments=True),
            cl.ExactMatch("surname"),
            cl.ExactMatch("city").configure(term_frequency_adjustments=True),
            cl.ExactMatch("email"),
        ],
        blocking_rules_to_generate_predictions=[
            block_on("first_name"),
            block_on("surname"),
        ],
        max_iterations=2,
        retain_intermediate_calculation_columns=True,
        retain_matching_columns=True,
    )

    # Compare df1 and df2
    res1_2_first, dummy = compare_records(df1, df2, settings, db_api)
    dummies.append(dummy)
    res1_2_first = res1_2_first.as_pandas_dataframe()
    res1_2_not_from_cache, dummy = compare_records(
        df1, df2, settings, db_api, use_sql_from_cache=False
    )
    dummies.append(dummy)
    res1_2_not_from_cache = res1_2_not_from_cache.as_pandas_dataframe()
    res1_2_from_cache, dummy = compare_records(
        df1, df2, settings, db_api, use_sql_from_cache=True
    )
    dummies.append(dummy)
    res1_2_from_cache = res1_2_from_cache.as_pandas_dataframe()

    # Compare match weights using pandas merge
    merged = res1_2_first.merge(
        res1_2_not_from_cache,
        on=["unique_id_l", "unique_id_r"],
        suffixes=("_first", "_not_cache"),
    )
    pd.testing.assert_series_equal(
        merged["match_weight_first"],
        merged["match_weight_not_cache"],
        check_names=False,
    )

    merged = res1_2_first.merge(
        res1_2_from_cache,
        on=["unique_id_l", "unique_id_r"],
        suffixes=("_first", "_from_cache"),
    )
    pd.testing.assert_series_equal(
        merged["match_weight_first"],
        merged["match_weight_from_cache"],
        check_names=False,
    )

    res1_3_first, dummy = compare_records(df1, df3, settings, db_api)
    dummies.append(dummy)
    res1_3_first = res1_3_first.as_pandas_dataframe()
    res1_3_not_from_cache, dummy = compare_records(
        df1, df3, settings, db_api, use_sql_from_cache=False
    )
    dummies.append(dummy)
    res1_3_not_from_cache = res1_3_not_from_cache.as_pandas_dataframe()
    res1_3_from_cache, dummy = compare_records(
        df1, df3, settings, db_api, use_sql_from_cache=True
    )
    dummies.append(dummy)
    res1_3_from_cache = res1_3_from_cache.as_pandas_dataframe()

    merged = res1_3_first.merge(
        res1_3_not_from_cache,
        on=["unique_id_l", "unique_id_r"],
        suffixes=("_first", "_not_cache"),
    )
    pd.testing.assert_series_equal(
        merged["match_weight_first"],
        merged["match_weight_not_cache"],
        check_names=False,
    )

    merged = res1_3_first.merge(
        res1_3_from_cache,
        on=["unique_id_l", "unique_id_r"],
        suffixes=("_first", "_from_cache"),
    )
    pd.testing.assert_series_equal(
        merged["match_weight_first"],
        merged["match_weight_from_cache"],
        check_names=False,
    )


@mark_with_dialects_excluding()
def test_realtime_cache_different_settings(test_helpers, dialect):
    helper = test_helpers[dialect]
    db_api = helper.extra_linker_args()["db_api"]

    df1 = pd.DataFrame(
        [
            {
                "unique_id": 0,
                "first_name": "Julia",
                "surname": "Taylor",
                "city": "London",
                "email": "julia@email.com",
            }
        ]
    )

    df2 = pd.DataFrame(
        [
            {
                "unique_id": 1,
                "first_name": "Julia",
                "surname": "Taylor",
                "city": "London",
                "email": "bad@address.com",
            }
        ]
    )

    settings_1 = SettingsCreator(
        link_type="dedupe_only",
        comparisons=[
            cl.ExactMatch("first_name"),
            cl.ExactMatch("surname"),
            cl.ExactMatch("city"),
        ],
        blocking_rules_to_generate_predictions=[block_on("first_name")],
    )

    settings_2 = SettingsCreator(
        link_type="dedupe_only",
        comparisons=[
            cl.ExactMatch("first_name"),
            cl.ExactMatch("surname"),
            cl.ExactMatch("email"),
        ],
        blocking_rules_to_generate_predictions=[block_on("first_name")],
    )

    res1, dummy = compare_records(df1, df2, settings_1, db_api, use_sql_from_cache=True)
    dummies.append(dummy)
    res1 = res1.as_record_dict()[0]["match_weight"]

    res2, dummy = compare_records(df1, df2, settings_2, db_api, use_sql_from_cache=True)
    dummies.append(dummy)
    res2 = res2.as_record_dict()[0]["match_weight"]

    assert res1 != pytest.approx(res2)

    res1_again, dummy = compare_records(
        df1, df2, settings_1, db_api, use_sql_from_cache=True
    )
    dummies.append(dummy)
    res1_again = res1_again.as_record_dict()[0]["match_weight"]
    assert res1 == pytest.approx(res1_again)

    print(dummies)  # noqa: T201
    assert True not in dummies


@mark_with_dialects_excluding()
def test_realtime_cache_different_settings_dict(test_helpers, dialect):
    helper = test_helpers[dialect]
    db_api = helper.extra_linker_args()["db_api"]

    df1 = pd.DataFrame(
        [
            {
                "unique_id": 0,
                "first_name": "Julia",
                "surname": "Taylor",
                "city": "London",
                "email": "julia@email.com",
            }
        ]
    )

    df2 = pd.DataFrame(
        [
            {
                "unique_id": 1,
                "first_name": "Julia",
                "surname": "Taylor",
                "city": "London",
                "email": "bad@address.com",
            }
        ]
    )

    settings_1 = {
        "link_type": "dedupe_only",
        "comparisons": [
            cl.ExactMatch("first_name"),
            cl.ExactMatch("surname"),
            cl.ExactMatch("city"),
        ],
        "blocking_rules_to_generate_predictions": [block_on("first_name")],
    }

    settings_2 = {
        "link_type": "dedupe_only",
        "comparisons": [
            cl.ExactMatch("first_name"),
            cl.ExactMatch("surname"),
            cl.ExactMatch("email"),
        ],
        "blocking_rules_to_generate_predictions": [block_on("first_name")],
    }

    res1, dummy = compare_records(df1, df2, settings_1, db_api, use_sql_from_cache=True)
    dummies.append(dummy)
    res1 = res1.as_record_dict()[0]["match_weight"]

    res2, dummy = compare_records(df1, df2, settings_2, db_api, use_sql_from_cache=True)
    dummies.append(dummy)
    res2 = res2.as_record_dict()[0]["match_weight"]

    assert res1 != pytest.approx(res2)

    res1_again, dummy = compare_records(
        df1, df2, settings_1, db_api, use_sql_from_cache=True
    )
    dummies.append(dummy)
    res1_again = res1_again.as_record_dict()[0]["match_weight"]
    assert res1 == pytest.approx(res1_again)

    print(dummies)  # noqa: T201
    assert True not in dummies
