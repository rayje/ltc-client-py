#!/opt/python3.3/bin/python3.3

import http.client, time
from time import sleep
import math, sys

def getPercentile(p, results):
	percentile = 0.0

	r = (float(len(results)) + 1.0) * p
	ir = float(math.floor(r))
	fr = r - ir

	v1 = float(results[int(ir)-1])

	if fr > 0.0 and ir < float(len(results)):
		v2 = float(results[int(ir)])
		percentile = (v2 - v1) * fr + v1
	else:
		percentile = v1

	return percentile

def stdDev(results, mean, total):
	diffs  = 0.0
	m = float(mean)

	for result in results:
		diffs += math.pow(1000000000.0 - m, 2)

	variance = diffs / total
	stdDev = math.sqrt(variance)

	return stdDev

numRequests = int(sys.argv[1])
results = []
conn = http.client.HTTPConnection("ltc-lbr.openclass.com")

for i in range(numRequests):
	start = time.monotonic()
	conn.request("GET", "/med")
	r1 = conn.getresponse()

	total = (time.monotonic() - start) * 1000000000
	results.append(total)
	r1.read()

	sleep(10)

# Report results
min = 1000000000 * 60 * 60
max = 0
totalRtt = 0
for result in results:
	totalRtt += result
	if result < min:
		min = result
	if result > max:
		max = result

mean = (totalRtt / len(results)) / 1000000
stddev = stdDev(results, mean, totalRtt) / 1000000
min = min / 1000000
max = max / 1000000
totalRtt = totalRtt / 1000000

results.sort()
_25m  = getPercentile(0.25, results) / 1000000
_75m  = getPercentile(0.75, results) / 1000000
_95m  = getPercentile(0.95, results) / 1000000
_99m  = getPercentile(0.99, results) / 1000000
_999m = getPercentile(0.999, results) / 1000000


print("="*30)
print("Requests:", len(results))

print("Latencies:")
print("\tTotal:     {0:.5f}\n".format(totalRtt))

print("\t0.25:\t{0:.5f}ms".format(_25m))
print("\t0.75:\t{0:.5f}ms".format(_75m))
print("\t0.95:\t{0:.5f}ms".format(_95m))
print("\t0.99:\t{0:.5f}ms".format(_99m))
print("\t0.999:\t{0:.5f}ms\n".format(_999m))

print("Distribution:")
print("\tmean:\t{0:.5f}ms".format(mean))
print("\tstd:\t{0:.5f}ms".format(stddev))
print("\tmin:\t{0:.5f}ms".format(min))
print("\tmax:\t{0:.5f}ms".format(max))
print("\tiqr:\t{0:.5f}ms".format(_75m - _25m))

print("="*30)


with open("results.txt", "wt") as out_file:
	for result in results:
		out_file.write(str(result) + '\n')
