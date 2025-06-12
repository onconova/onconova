from enum import Enum


class Age(int):
    pass


class Username(str):
    pass


class AgeBin(str, Enum):
    SUB_20 = "<20"
    AGE_20_24 = "20-24"
    AGE_25_30 = "25-30"
    AGE_30_34 = "30-34"
    AGE_35_40 = "35-40"
    AGE_40_44 = "40-44"
    AGE_45_50 = "45-50"
    AGE_50_54 = "50-54"
    AGE_55_60 = "55-60"
    AGE_60_64 = "60-64"
    AGE_65_70 = "65-70"
    AGE_70_74 = "70-74"
    AGE_75_80 = "75-80"
    AGE_80_84 = "80-84"
    AGE_85_90 = "85-90"
    OVER_90 = ">90"
