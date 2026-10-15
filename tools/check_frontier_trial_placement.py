"""Pinned linear random-spread parity and isolation checks; no world mutation."""
from run_frontier_natural_validation import ROOT,LegacyRandom,candidate,TARGET,check_candidates

random=LegacyRandom(0)
assert [random.integer(24) for _ in range(2)]==[0,4]
assert LegacyRandom(0).integer(16)==11
assert TARGET[0]//32==-3 and TARGET[1]//32==1
assert candidate(-3,1)==TARGET
result=check_candidates(ROOT/'server/validation-inland-terrain-baseline-20261014')
print('FRONTIER TRIAL PLACEMENT PASS:',result)
