import sys

from trace_route_util import trace_route

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Incorrect number of input arguments, only one parameter is required.\n")
        print(len(sys.argv))
        exit(1)
    trace_route(sys.argv[1])
