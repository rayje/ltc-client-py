#!/usr/bin/env python

import http.client, time
from time import sleep
import math, sys

SECOND=1000000000
MILLISECOND=1000000
MICROSECOND=1000

def calcToString(calc):
    if calc >= SECOND:
        calc = calc/SECOND
        return "{:.5f}s".format(calc)
    elif calc >= MILLISECOND:
        calc = calc/MILLISECOND
        return "{:.5f}ms".format(calc)
    elif calc >= MICROSECOND: 
        calc = calc/MICROSECOND
        return "{:.5f}us".format(calc)
    else:
        return "{:.5f}ns".format(calc)

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

def run(host, numRequests):
    conn = http.client.HTTPConnection(host)
    results = []

    for i in range(numRequests):
        start = time.monotonic()
        conn.request("GET", "/med")
        r1 = conn.getresponse()

        total = (time.monotonic() - start) * 1000000000
        results.append(total)
        r1.read()

        sleep(10)

    return results

def report(results):
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

    mean = (totalRtt / len(results))
    stddev = stdDev(results, mean, totalRtt)
    totalRtt = totalRtt

    results.sort()
    _25m  = getPercentile(0.25, results)
    _75m  = getPercentile(0.75, results)
    _95m  = getPercentile(0.95, results)
    _99m  = getPercentile(0.99, results)
    _999m = getPercentile(0.999, results)

    print("="*30)
    print("Requests:", len(results))

    print("Latencies:")
    print("\tTotal:     {0}\n".format(calcToString(totalRtt)))

    print("\t0.25:\t{0}".format(calcToString(_25m)))
    print("\t0.75:\t{0}".format(calcToString(_75m)))
    print("\t0.95:\t{0}".format(calcToString(_95m)))
    print("\t0.99:\t{0}".format(calcToString(_99m)))
    print("\t0.999:\t{0}\n".format(calcToString(_999m)))

    print("Distribution:")
    print("\tmean:\t{0}".format(calcToString(mean)))
    print("\tstd:\t{0}".format(calcToString(stddev)))
    print("\tmin:\t{0}".format(calcToString(min)))
    print("\tmax:\t{0}".format(calcToString(max)))
    print("\tiqr:\t{0}".format(calcToString(_75m - _25m)))

    print("="*30)

def dumpToFile(results):
    with open("results.txt", "wt") as out_file:
        for result in results:
            out_file.write(str(result) + '\n')

def usage():
    print("usage: ./client.py <host> <num-requests>")

if __name__ == "__main__":
    if len(sys.argv) != 3:
        usage()
        sys.exit(1)

    host = sys.argv[1]
    numRequests = int(sys.argv[2])

    results = run(host, numRequests)
    dumpToFile(results)
    report(results)

