import coverage
import unittest

if __name__ == '__main__':
    cov = coverage.Coverage(source=["..\\src"])
    cov.start()

    try:
        testsuite = unittest.TestLoader().discover('.')
        unittest.TextTestRunner(verbosity=1).run(testsuite)
    except:  # catch-all except clause
        pass

    cov.stop()
    cov.save()

    cov.html_report()
    print("Done.")