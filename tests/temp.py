import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '../'))
from scheduleduty import scheduleduty  # NOQA

print "ITS ALIVE!!!!!"
importer = scheduleduty.Import("weekly_shifts","./examples/weekly_shifts","5MWsivLGsyxz3zS17Mpx","Weekly Shifts","Level","Multi","2017-01-01","2017-02-01","UTC",1,30)
import2 = scheduleduty.Import("standard_rotation","./examples/standard_rotation","5MWsivLGsyxz3zS17Mpx","Standard Rotation",None,None,"2017-01-01","2017-02-01","UTC",None,None)
importer.execute()
import2.execute()
