from enum import Enum


class Age(int):
    pass


class Username(str):
    pass


class Array(list):
    pass


class AgeBin(str, Enum):
    SUB_20 = "<20"
    AGE_20_24 = "20-24"
    AGE_25_29 = "25-29"
    AGE_30_34 = "30-34"
    AGE_35_39 = "35-39"
    AGE_40_44 = "40-44"
    AGE_45_49 = "45-49"
    AGE_50_54 = "50-56"
    AGE_55_59 = "55-59"
    AGE_60_64 = "60-64"
    AGE_65_69 = "65-69"
    AGE_70_74 = "70-74"
    AGE_75_79 = "75-79"
    AGE_80_84 = "80-84"
    AGE_85_89 = "85-89"
    OVER_90 = "90+"

    def __str__(self):
        return self.value
