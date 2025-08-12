from pytest import mark

from splink import block_on

from .basic_settings import get_settings_dict
from .decorator import mark_with_dialects_excluding


@mark.no_df_backend
@mark_with_dialects_excluding("postgres", "sqlite")
def test_run_with_no_df_backend(dialect, test_helpers):
    helper = test_helpers[dialect]

    df = helper.load_frame_from_csv("./tests/datasets/fake_1000_from_splink_demos.csv")
    settings_dict = get_settings_dict()
    settings_dict["blocking_rules_to_generate_predictions"] = ["l.surname = r.surname"]
    linker = helper.Linker(df, settings_dict, **helper.extra_linker_args())

    # linker.training.estimate_u_using_random_sampling(max_pairs=1e6)
    # linker.training.estimate_parameters_using_expectation_maximisation(
    #     block_on("first_name", "surname")
    # )
    # linker.training.estimate_parameters_using_expectation_maximisation(block_on("email"))

    pairwise_predictions = linker.inference.predict(threshold_match_weight=-5)

    linker.clustering.cluster_pairwise_predictions_at_threshold(
        pairwise_predictions, 0.95
    )

