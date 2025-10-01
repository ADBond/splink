import pytest

from splink import block_on
from splink.blocking_analysis import (
    count_comparisons_from_blocking_rule,
    cumulative_comparisons_to_be_scored_from_blocking_rules_chart,
    cumulative_comparisons_to_be_scored_from_blocking_rules_data,
)

from ..basic_settings import get_settings_dict
from ..decorator import mark_with_dialects_excluding

df_backend_params = [
    pytest.param("polars", marks=pytest.mark.polars),
    pytest.param("pandas", marks=pytest.mark.pandas),
    pytest.param("pyarrow", marks=pytest.mark.pyarrow),
]


# exclude postgres + sqlite as (for now) we rely on pandas for loading csv files
@pytest.mark.no_df_backend
@mark_with_dialects_excluding("postgres", "sqlite")
def test_run_with_no_df_backend(dialect, test_helpers):
    helper = test_helpers[dialect]

    df = helper.load_frame_from_csv("./tests/datasets/fake_1000_from_splink_demos.csv")
    settings_dict = get_settings_dict()
    settings_dict["blocking_rules_to_generate_predictions"] = ["l.surname = r.surname"]
    linker = helper.Linker(df, settings_dict, **helper.extra_linker_args())

    pairwise_predictions = linker.inference.predict(threshold_match_weight=-5)

    linker.clustering.cluster_pairwise_predictions_at_threshold(
        pairwise_predictions, 0.95
    )


@pytest.mark.parametrize("df_backend", df_backend_params)
@mark_with_dialects_excluding("postgres", "sqlite")
def test_quickstart_particular_df_backend(dialect, test_helpers, df_backend):
    helper = test_helpers[dialect]

    df = helper.load_frame_from_csv("./tests/datasets/fake_1000_from_splink_demos.csv")
    settings_dict = get_settings_dict()
    settings_dict["blocking_rules_to_generate_predictions"] = ["l.surname = r.surname"]

    db_api = helper.DatabaseAPI(**helper.db_api_args())
    db_api.df_backend = df_backend

    linker = helper.Linker(df, settings_dict, db_api)

    linker.training.estimate_probability_two_random_records_match(
        [block_on("first_name", "surname")],
        recall=0.7,
    )
    linker.training.estimate_u_using_random_sampling(max_pairs=1e6)
    linker.training.estimate_parameters_using_expectation_maximisation(
        block_on("first_name", "surname")
    )
    linker.training.estimate_parameters_using_expectation_maximisation(
        block_on("email")
    )

    pairwise_predictions = linker.inference.predict(threshold_match_weight=-5)

    linker.clustering.cluster_pairwise_predictions_at_threshold(
        pairwise_predictions, 0.95
    )


@pytest.mark.parametrize("df_backend", df_backend_params)
@mark_with_dialects_excluding("postgres", "sqlite")
def test_blocking_analysis_df_backend(dialect, test_helpers, df_backend):
    helper = test_helpers[dialect]
    db_api = helper.DatabaseAPI(**helper.db_api_args())
    db_api.df_backend = df_backend

    df = helper.load_frame_from_csv("./tests/datasets/fake_1000_from_splink_demos.csv")

    count_comparisons_from_blocking_rule(
        table_or_tables=df,
        blocking_rule=block_on("surname"),
        link_type="dedupe_only",
        db_api=db_api,
        unique_id_column_name="unique_id",
    )
    cumulative_comparisons_to_be_scored_from_blocking_rules_chart(
        table_or_tables=df,
        blocking_rules=block_on("first_name"),
        link_type="dedupe_only",
        db_api=db_api,
    )
    cumulative_comparisons_to_be_scored_from_blocking_rules_data(
        table_or_tables=df,
        blocking_rules=block_on("first_name"),
        link_type="dedupe_only",
        db_api=db_api,
    )
