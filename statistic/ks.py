from scipy.stats import ks_2samp, kstest
import pandas as pd


def ks_test(data1: list[float], data2: list[float], alpha: float):
    test = ks_2samp(data1, data2)
    pvalue, statistic = test.pvalue, test.statistic


def count_critical_value(len1: int, len2: int, alpha: float) -> float:
    pass
