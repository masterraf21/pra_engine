import math

from scipy.stats import ks_2samp
from src.utils.logging import get_logger

from .constants import C_ALPHA

logger = get_logger(__name__)


def ks_test_same_dist(data1: list[float], data2: list[float],
                      alpha: float, debug: bool = False) -> bool:

    test = ks_2samp(data1, data2)
    critical_value = count_critical_value(len(data1), len(data2), alpha)
    pvalue, statistic = test.pvalue, test.statistic

    if debug:
        logger.debug(f"result: {test}")
        logger.debug(f"Critical Value: {critical_value}")

    if pvalue < alpha:
        if debug:
            logger.debug(f"pvalue: {pvalue}, α: {alpha}")
            logger.debug("pvalue < α: different distribution, returning False")
        return False

    # if statistic > crit vale : different dist
    # if statistic < crit value: same dist
    if debug:
        if statistic > critical_value:
            logger.debug("statistic > crit value: different disttribution, returning False")
        else:
            logger.debug("statistic < crit value: same distribution, returning True")
    return statistic < critical_value


def count_critical_value(n1: int, n2: int, alpha: float) -> float:
    if alpha not in C_ALPHA:
        raise ValueError("Alpha not available")
    c_alpha = C_ALPHA[alpha]
    return c_alpha*math.sqrt((n1+n2)/n1*n2)
