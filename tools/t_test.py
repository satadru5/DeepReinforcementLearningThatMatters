import scipy.stats as stats
import random
import pandas as pd
import numpy as np
import bootstrapped.bootstrap as bas
import bootstrapped.stats_functions as bs_stats
import bootstrapped.compare_functions as bs_compare
import bootstrapped.power as bs_power
import argparse
parser = argparse.ArgumentParser()
parser.add_argument("paths_to_progress_csvs", nargs="+", help="All the csvs")
parser.add_argument("--range_start", type=int, default=-1)
parser.add_argument("--range_end", type=int, default=100000000)

from scipy.stats import ks_2samp

args = parser.parse_args()

assert len(args.paths_to_progress_csvs) == 2

data = np.load(args.paths_to_progress_csvs[0])
data2 = np.load(args.paths_to_progress_csvs[1])

final_average_return = np.array(sorted(data[-1])) 
final_average_return2 = np.array(sorted(data2[-1]))

print("Average Returns 1: ", final_average_return)
print("Average Returns 2", final_average_return2)


#print(t_test(len(final_average_return), np.array(final_average_return) - np.array(final_average_return2), 2e6, 5000))
print("t-test", stats.ttest_ind(final_average_return, final_average_return2))
print("ks-2sample", ks_2samp(final_average_return, final_average_return2))

def run_simulation(data):
     lift = 1.25
     results = []
     for i in range(3000):
         random.shuffle(data)
         test = data[:len(data)/2] * lift
         ctrl = data[len(data)/2:]
         results.append(bas.bootstrap_ab(test, ctrl, bs_stats.mean, bs_compare.percent_change))
     return results

def run_simulation2(data, data2):
     results = []
     for i in range(3000):
         results.append(bas.bootstrap_ab(data, data2, bs_stats.mean, bs_compare.percent_change))
     return results

print("bootstrap a/b", bas.bootstrap_ab(final_average_return, final_average_return2, bs_stats.mean, bs_compare.percent_change))
bab=  bas.bootstrap_ab(final_average_return, final_average_return2, bs_stats.mean, bs_compare.percent_change)
x = run_simulation2(final_average_return, final_average_return2)
bootstrap_ab = bs_power.power_stats(x)
print("power analysis bootstrap a/b") 
print(bootstrap_ab)

print("****Power1****")
test_results = run_simulation(final_average_return)
print(bs_power.power_stats(test_results))
print("****Power2****")
test_results = run_simulation(final_average_return2)
print(bs_power.power_stats(test_results))

print("***Bootstrap1****")
sim = bas.bootstrap(final_average_return, stat_func=bs_stats.mean)
print("%.2f (%.2f, %.2f)" % (sim.value, sim.lower_bound, sim.upper_bound))
print("***Bootstrap2****")
sim = bas.bootstrap(final_average_return2, stat_func=bs_stats.mean)
print("%.2f (%.2f, %.2f)" % (sim.value, sim.lower_bound, sim.upper_bound))

print("***Power1****")
sim = run_simulation(final_average_return)
sim = bs_power.power_stats(sim)
print("\\shortstack{%.2f \\%%\\\\%.2f \\%% \\\\ %.2f \\%%}" % (sim.transpose()["Insignificant"], sim.transpose()["Positive Significant"], sim.transpose()["Negative Significant"]))
print("***Power2****")
sim = run_simulation(final_average_return2)
sim = bs_power.power_stats(sim)
#sim = bas.bootstrap(final_average_return2, stat_func=bs_stats.mean)
print("\\shortstack{%.2f \\%% \\\\ %.2f \\%% \\\\ %.2f \\%%}" % (sim.transpose()["Insignificant"], sim.transpose()["Positive Significant"], sim.transpose()["Negative Significant"]))

t,p = stats.ttest_ind(final_average_return, final_average_return2)
ks,kp =ks_2samp(final_average_return, final_average_return2)

a, b,c = bab.value, bab.lower_bound, bab.upper_bound

if bootstrap_ab.transpose()["Positive Significant"][0] >= bootstrap_ab.transpose()["Negative Significant"][0]:
    boot = "+%.2f" % bootstrap_ab.transpose()["Positive Significant"]
else:
    boot = "-%.2f" % bootstrap_ab.transpose()["Negative Significant"]
print("\\shortstack{$t=%.2f,p=%.3f$\\\\$KS=%.2f,p=%.3f$\\\\%.2f \\%% (%.2f \\%%, %.2f \\%%) }" % (t,p,ks,kp,a,b,c))



