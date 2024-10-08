from functools import cache

import polars as pl
from django.shortcuts import render
from great_tables import GT, html
from great_tables.data import sza


@cache
def get_sza():
    return pl.from_pandas(sza)


def index(request):
    sza_pivot = (
        get_sza()
        .filter((pl.col("latitude") == "20") & (pl.col("tst") <= "1200"))
        .select(pl.col("*").exclude("latitude"))
        .drop_nulls()
        .pivot(values="sza", index="month", on="tst", sort_columns=True)
    )

    sza_gt = (
        GT(sza_pivot, rowname_col="month")
        .data_color(
            domain=[90, 0],
            palette=["rebeccapurple", "white", "orange"],
            na_color="white",
        )
        .tab_header(
            title="Solar Zenith Angles from 05:30 to 12:00",
            subtitle=html("Average monthly values at latitude of 20&deg;N."),
        )
        .sub_missing(missing_text="")
    )

    context = {"sza_gt": sza_gt.as_raw_html()}

    return render(request, "gt/index.html", context)
