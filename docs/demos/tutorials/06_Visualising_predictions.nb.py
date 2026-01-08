# ---
# jupyter:
#   jupytext:
#     text_representation:
#       extension: .py
#       format_name: percent
#       format_version: '1.3'
#       jupytext_version: 1.18.1
#   kernelspec:
#     display_name: Python 3 (ipykernel)
#     language: python
#     name: python3
# ---

# %% [markdown]
# # Visualising predictions
#
# <a target="_blank" href="https://colab.research.google.com/github/moj-analytical-services/splink/blob/master/docs/demos/tutorials/06_Visualising_predictions.ipynb">
#   <img src="https://colab.research.google.com/assets/colab-badge.svg" alt="Open In Colab"/>
# </a>
#
# Splink contains a variety of tools to help you visualise your predictions.
#
# The idea is that, by developing an understanding of how your model works, you can gain confidence that the predictions it makes are sensible, or alternatively find examples of where your model isn't working, which may help you improve the model specification and fix these problems.
#

# %% tags=["hide_input"]
# Uncomment and run this cell if you're running in Google Colab.
# # !pip install splink

# %%
# Rerun our predictions to we're ready to view the charts
from splink import Linker, DuckDBAPI, splink_datasets

import pandas as pd

pd.options.display.max_columns = 1000

db_api = DuckDBAPI()
df = splink_datasets.fake_1000

# %%
import json
import urllib

url = "https://raw.githubusercontent.com/moj-analytical-services/splink/847e32508b1a9cdd7bcd2ca6c0a74e547fb69865/docs/demos/demo_settings/saved_model_from_demo.json"

with urllib.request.urlopen(url) as u:
    settings = json.loads(u.read().decode())


linker = Linker(df, settings, db_api=DuckDBAPI())
df_predictions = linker.inference.predict(threshold_match_probability=0.2)

# %% [markdown]
# ## Waterfall chart
#
# The waterfall chart provides a means of visualising individual predictions to understand how Splink computed the final matchweight for a particular pairwise record comparison.
#
# To plot a waterfall chart, the user chooses one or more records from the results of `linker.inference.predict()`, and provides these records to the [`linker.visualisations.waterfall_chart()`](../../api_docs/visualisations.md#splink.internals.linker_components.visualisations.LinkerVisualisations.waterfall_chart) function.
#
# For an introduction to waterfall charts and how to interpret them, please see [this](https://www.youtube.com/watch?v=msz3T741KQI&t=507s) video.
#

# %%
records_to_view = df_predictions.as_record_dict(limit=5)
linker.visualisations.waterfall_chart(records_to_view, filter_nulls=False)

# %% [markdown]
# ## Comparison viewer dashboard
#
# The [comparison viewer dashboard](../../api_docs/visualisations.md#splink.internals.linker_components.visualisations.LinkerVisualisations.comparison_viewer_dashboard) takes this one step further by producing an interactive dashboard that contains example predictions from across the spectrum of match scores.
#
# An in-depth video describing how to interpret the dashboard can be found [here](https://www.youtube.com/watch?v=DNvCMqjipis).
#

# %%
linker.visualisations.comparison_viewer_dashboard(df_predictions, "scv.html", overwrite=True)

# You can view the scv.html file in your browser, or inline in a notbook as follows
from IPython.display import IFrame

IFrame(src="./scv.html", width="100%", height=1200)

# %% [markdown]
# ## Cluster studio dashboard
#
# Cluster studio is an interactive dashboards that visualises the results of clustering your predictions.
#
# It provides examples of clusters of different sizes. The shape and size of clusters can be indicative of problems with record linkage, so it provides a tool to help you find potential false positive and negative links.
#

# %%
df_clusters = linker.clustering.cluster_pairwise_predictions_at_threshold(
    df_predictions, threshold_match_probability=0.5
)

linker.visualisations.cluster_studio_dashboard(
    df_predictions,
    df_clusters,
    "cluster_studio.html",
    sampling_method="by_cluster_size",
    overwrite=True,
)

# You can view the scv.html file in your browser, or inline in a notbook as follows
from IPython.display import IFrame

IFrame(src="./cluster_studio.html", width="100%", height=1000)

# %% [markdown]
# !!! note "Further Reading"
#
#     :material-tools: For more on the visualisation tools in Splink, please refer to the [Visualisation API documentation](../../api_docs/visualisations.md).
#
#     :bar_chart: For more on the charts used in this tutorial, please refer to the [Charts Gallery](../../charts/index.md#model-evaluation).
#

# %% [markdown]
# ## Next steps
#
# Now we have visualised the results of a model, we can move on to some more formal Quality Assurance procedures using labelled data.
#
