import logging
from collections import UserDict
from copy import copy
from typing import TYPE_CHECKING

from .splink_dataframe import SplinkDataFrame

logger = logging.getLogger(__name__)

if TYPE_CHECKING:
    TypedUserDict = UserDict[str, SplinkDataFrame]
else:
    TypedUserDict = UserDict


class CacheDictWithLogging(TypedUserDict):
    def __init__(self) -> None:
        super().__init__()
        self.executed_queries: list[SplinkDataFrame] = []
        self.queries_retrieved_from_cache: list[SplinkDataFrame] = []

    def __getitem__(self, key: str) -> SplinkDataFrame:
        splink_dataframe = super().__getitem__(key)

        # Return a copy so that user can modify physical or templated name
        # without modifying the version in the cache
        return copy(splink_dataframe)

    def __setitem__(self, key: str, value: SplinkDataFrame) -> None:
        if not isinstance(value, SplinkDataFrame):
            raise TypeError("Cached items must be of type SplinkDataFrame")

        super().__setitem__(key, value)

        logger.log(
            1, f"Setting cache for {key}" f" with physical name {value.physical_name}"
        )

    def invalidate_cache(self) -> None:
        self.data = dict()

    def get_with_logging(self, key: str) -> SplinkDataFrame:
        df = self[key]
        phy_name = df.physical_name
        logger.debug(
            f"Using cache for template name {key}" f" with physical name {phy_name}"
        )
        self.queries_retrieved_from_cache.append(df)

        return df

    def reset_executed_queries_tracker(self) -> None:
        self.executed_queries = []

    def is_in_executed_queries(
        self,
        name_to_find: str,
        search_physical: bool = True,
        search_templated: bool = True,
    ) -> bool:
        names = []
        for df in self.executed_queries:
            if search_physical:
                names.append(df.physical_name)
            if search_templated:
                names.append(df.templated_name)

        return name_to_find in names

    def reset_queries_retrieved_from_cache_tracker(self) -> None:
        self.queries_retrieved_from_cache = []

    def is_in_queries_retrieved_from_cache(
        self,
        name_to_find: str,
        search_physical: bool = True,
        search_templated: bool = True,
    ) -> bool:
        names = []
        for df in self.queries_retrieved_from_cache:
            if search_physical:
                names.append(df.physical_name)
            if search_templated:
                names.append(df.templated_name)

        return name_to_find in names
