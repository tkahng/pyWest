def Profiler(OriginalFunction):
    import time
    def WrapperFunction(*args, **kwargs):
        startTime = time.time()
        results = OriginalFunction(*args, **kwargs)
        endTime = round(time.time() - startTime, 3)
        print("{0} ran in {1} sec".format(OriginalFunction.__name__, endTime))
        return(results)
    return(WrapperFunction)