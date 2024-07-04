import sys
if sys.prefix == '/usr':
    sys.real_prefix = sys.prefix
    sys.prefix = sys.exec_prefix = '/home/sukruthi/Desktop/Start-up/Developer/ObjectTrackingUsingEyeGaze/env_ws/install/env_setup'
